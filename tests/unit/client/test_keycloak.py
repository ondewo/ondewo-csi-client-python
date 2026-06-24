# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Hermetic unit tests for the D18 headless Keycloak token managers.

A fake in-memory transport records every form body sent to the (mocked) Keycloak token
endpoint and returns scripted JSON responses, so no network or real ``requests``/``aiohttp``
call is made.
"""
from typing import (
    Any,
    Dict,
    List,
)

import pytest

from ondewo.csi.client.utils.keycloak import (
    AsyncKeycloakTokenManager,
    KeycloakAuthError,
    KeycloakTokenManager,
    _default_async_transport,
    _default_sync_transport,
    build_token_endpoint,
)

KEYCLOAK_URL = "https://keycloak.ondewo.com/auth"
REALM = "ondewo-ccai-platform"
CLIENT_ID = "ondewo-nlu-cai-sdk-public"
USERNAME = "tech-user@ondewo.com"
PASSWORD = "s3cret"
EXPECTED_ENDPOINT = "https://keycloak.ondewo.com/auth/realms/ondewo-ccai-platform/protocol/openid-connect/token"


class FakeTransport:
    """Records requests and replays scripted responses (no network)."""

    def __init__(self, responses: List[Dict[str, Any]]) -> None:
        self._responses = list(responses)
        self.requests: List[Dict[str, str]] = []
        self.urls: List[str] = []

    def _next(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        self.urls.append(url)
        self.requests.append(data)
        if not self._responses:
            raise AssertionError("FakeTransport ran out of scripted responses")
        return self._responses.pop(0)

    def sync(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        return self._next(url, data)

    async def async_(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        return self._next(url, data)


def _login_response(access: str = "access-1", refresh: str = "offline-1", expires_in: int = 300) -> Dict[str, Any]:
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }


def _sync_manager(transport: FakeTransport, **overrides: Any) -> KeycloakTokenManager:
    kwargs: Dict[str, Any] = {
        "keycloak_url": KEYCLOAK_URL,
        "realm": REALM,
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
        "transport": transport.sync,
    }
    kwargs.update(overrides)
    return KeycloakTokenManager(**kwargs)


# --------------------------------------------------------------------------------------- #
# Endpoint construction
# --------------------------------------------------------------------------------------- #
def test_build_token_endpoint_strips_trailing_slash() -> None:
    assert build_token_endpoint(KEYCLOAK_URL + "/", REALM) == EXPECTED_ENDPOINT
    assert build_token_endpoint(KEYCLOAK_URL, REALM) == EXPECTED_ENDPOINT


def test_manager_exposes_resolved_token_endpoint() -> None:
    transport = FakeTransport([])
    manager = _sync_manager(transport)

    assert manager.token_endpoint == EXPECTED_ENDPOINT


# --------------------------------------------------------------------------------------- #
# Sync manager
# --------------------------------------------------------------------------------------- #
def test_login_uses_ropc_password_grant_with_offline_access_and_no_secret() -> None:
    transport = FakeTransport([_login_response()])
    manager = _sync_manager(transport)

    manager.login()

    assert transport.urls == [EXPECTED_ENDPOINT]
    sent = transport.requests[0]
    assert sent["grant_type"] == "password"
    assert sent["scope"] == "offline_access"
    assert sent["client_id"] == CLIENT_ID
    assert sent["username"] == USERNAME
    assert sent["password"] == PASSWORD
    # Q1: PUBLIC client — no client_secret may be sent.
    assert "client_secret" not in sent


def test_get_authorization_metadata_returns_bearer_tuple() -> None:
    transport = FakeTransport([_login_response(access="jwt-abc")])
    manager = _sync_manager(transport)
    manager.login()

    key, value = manager.get_authorization_metadata()

    assert key == "authorization"
    assert value == "Bearer jwt-abc"


def test_fresh_access_token_is_reused_without_refresh() -> None:
    transport = FakeTransport([_login_response(access="jwt-fresh", expires_in=300)])
    manager = _sync_manager(transport)
    manager.login()

    first = manager.get_access_token()
    second = manager.get_access_token()

    assert first == "jwt-fresh"
    assert second == "jwt-fresh"
    # Only the login call hit the transport; no refresh.
    assert len(transport.requests) == 1


def test_expired_access_token_triggers_refresh_token_grant() -> None:
    transport = FakeTransport(
        [
            # expires_in below the skew window => immediately stale => next call refreshes.
            _login_response(access="jwt-old", refresh="offline-1", expires_in=0),
            _login_response(access="jwt-new", refresh="offline-2", expires_in=300),
        ]
    )
    manager = _sync_manager(transport)
    manager.login()

    token = manager.get_access_token()

    assert token == "jwt-new"
    refresh_request = transport.requests[1]
    assert refresh_request["grant_type"] == "refresh_token"
    assert refresh_request["refresh_token"] == "offline-1"
    assert refresh_request["client_id"] == CLIENT_ID
    assert "client_secret" not in refresh_request


def test_force_refresh_replays_even_when_token_fresh() -> None:
    transport = FakeTransport(
        [
            _login_response(access="jwt-1", refresh="offline-1", expires_in=300),
            _login_response(access="jwt-2", refresh="offline-1", expires_in=300),
        ]
    )
    manager = _sync_manager(transport)
    manager.login()

    refreshed = manager.get_access_token(force_refresh=True)

    assert refreshed == "jwt-2"
    assert transport.requests[1]["grant_type"] == "refresh_token"


def test_refresh_keeps_previous_offline_token_when_response_omits_it() -> None:
    transport = FakeTransport(
        [
            _login_response(access="jwt-1", refresh="offline-1", expires_in=0),
            # Refresh response without a new refresh_token: keep the offline token.
            {"access_token": "jwt-2", "expires_in": 0},
            {"access_token": "jwt-3", "expires_in": 300},
        ]
    )
    manager = _sync_manager(transport)
    manager.login()

    manager.get_access_token()  # forces first refresh, response omits refresh_token
    manager.get_access_token()  # forces second refresh, must reuse offline-1

    assert transport.requests[1]["refresh_token"] == "offline-1"
    assert transport.requests[2]["refresh_token"] == "offline-1"


def test_token_expiration_in_s_zero_stops_refresh_loop() -> None:
    # token_expiration_in_s=0 => the auto-refresh window is closed immediately after login.
    transport = FakeTransport([_login_response(access="jwt-old", expires_in=0)])
    manager = _sync_manager(transport, token_expiration_in_s=0)
    manager.login()

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.get_access_token()

    assert "token_expiration_in_s" in str(exc_info.value)
    # No refresh attempt was made.
    assert len(transport.requests) == 1


def test_no_token_expiration_bound_allows_unbounded_refresh() -> None:
    transport = FakeTransport(
        [
            _login_response(access="jwt-old", expires_in=0),
            _login_response(access="jwt-new", expires_in=300),
        ]
    )
    manager = _sync_manager(transport, token_expiration_in_s=None)
    manager.login()

    assert manager.get_access_token() == "jwt-new"


def test_get_access_token_before_login_raises() -> None:
    transport = FakeTransport([])
    manager = _sync_manager(transport)

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.get_access_token()

    assert "Not logged in" in str(exc_info.value)


def test_login_response_without_access_token_raises() -> None:
    transport = FakeTransport([{"error": "invalid_grant", "error_description": "bad creds"}])
    manager = _sync_manager(transport)

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.login()

    assert "bad creds" in str(exc_info.value)


def test_manager_rejects_empty_required_fields() -> None:
    with pytest.raises(ValueError):
        KeycloakTokenManager(
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id="",
            username=USERNAME,
            password=PASSWORD,
        )


# --------------------------------------------------------------------------------------- #
# Async manager (mirror of the load-bearing sync paths)
# --------------------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_async_login_uses_ropc_password_grant_with_offline_access() -> None:
    transport = FakeTransport([_login_response(access="jwt-async")])
    manager = AsyncKeycloakTokenManager(
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        transport=transport.async_,
    )

    await manager.login()
    key, value = await manager.get_authorization_metadata()

    assert key == "authorization"
    assert value == "Bearer jwt-async"
    sent = transport.requests[0]
    assert sent["grant_type"] == "password"
    assert sent["scope"] == "offline_access"
    assert "client_secret" not in sent


@pytest.mark.asyncio
async def test_async_expired_token_triggers_refresh() -> None:
    transport = FakeTransport(
        [
            _login_response(access="jwt-old", refresh="offline-1", expires_in=0),
            _login_response(access="jwt-new", refresh="offline-2", expires_in=300),
        ]
    )
    manager = AsyncKeycloakTokenManager(
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        transport=transport.async_,
    )

    await manager.login()
    token = await manager.get_access_token()

    assert token == "jwt-new"
    assert transport.requests[1]["grant_type"] == "refresh_token"
    assert transport.requests[1]["refresh_token"] == "offline-1"


@pytest.mark.asyncio
async def test_async_token_expiration_in_s_zero_stops_refresh() -> None:
    transport = FakeTransport([_login_response(access="jwt-old", expires_in=0)])
    manager = AsyncKeycloakTokenManager(
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        token_expiration_in_s=0,
        transport=transport.async_,
    )

    await manager.login()
    with pytest.raises(KeycloakAuthError):
        await manager.get_access_token()


# --------------------------------------------------------------------------------------- #
# Default HTTP transports (hermetic: the real requests/aiohttp clients are monkeypatched
# so no network call is made; only the SDK's status-code handling / JSON decoding is run).
# --------------------------------------------------------------------------------------- #
class _FakeRequestsResponse:
    """Minimal ``requests.Response`` stand-in for the default sync transport."""

    def __init__(self, status_code: int, body: Dict[str, Any]) -> None:
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self) -> Dict[str, Any]:
        return self._body


def test_default_sync_transport_returns_json_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import requests

    captured: Dict[str, Any] = {}

    def fake_post(url: str, data: Dict[str, str], timeout: int) -> _FakeRequestsResponse:
        captured["url"] = url
        captured["data"] = data
        captured["timeout"] = timeout
        return _FakeRequestsResponse(200, _login_response(access="jwt-sync"))

    monkeypatch.setattr(requests, "post", fake_post)

    result = _default_sync_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert result["access_token"] == "jwt-sync"
    assert captured["url"] == EXPECTED_ENDPOINT
    assert captured["data"] == {"grant_type": "password"}
    assert captured["timeout"] == 30


def test_default_sync_transport_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import requests

    def fake_post(url: str, data: Dict[str, str], timeout: int) -> _FakeRequestsResponse:
        return _FakeRequestsResponse(401, {"error": "invalid_grant"})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(KeycloakAuthError) as exc_info:
        _default_sync_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert "401" in str(exc_info.value)


class _FakeAiohttpResponse:
    """Async-context-manager response stand-in for the default async transport."""

    def __init__(self, status: int, body: Dict[str, Any]) -> None:
        self.status = status
        self._body = body

    async def __aenter__(self) -> "_FakeAiohttpResponse":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    async def json(self) -> Dict[str, Any]:
        return self._body

    async def text(self) -> str:
        return str(self._body)


class _FakeAiohttpSession:
    """``aiohttp.ClientSession`` stand-in returning a scripted response."""

    def __init__(self, response: _FakeAiohttpResponse) -> None:
        self._response = response

    async def __aenter__(self) -> "_FakeAiohttpSession":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        return None

    def post(self, url: str, data: Dict[str, str], timeout: Any) -> _FakeAiohttpResponse:
        return self._response


@pytest.mark.asyncio
async def test_default_async_transport_returns_json_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import aiohttp

    response = _FakeAiohttpResponse(200, _login_response(access="jwt-async-default"))
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: _FakeAiohttpSession(response))

    result = await _default_async_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert result["access_token"] == "jwt-async-default"


@pytest.mark.asyncio
async def test_default_async_transport_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import aiohttp

    response = _FakeAiohttpResponse(500, {"error": "server_error"})
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: _FakeAiohttpSession(response))

    with pytest.raises(KeycloakAuthError) as exc_info:
        await _default_async_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert "500" in str(exc_info.value)
