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
    """
    In-memory HTTP transport double that records requests and replays scripted responses.

    Used to exercise the token managers fully offline: each call appends the target URL and
    the form body to public lists for assertions, then returns the next scripted JSON
    response in order. Both a sync (:meth:`sync`) and an async (:meth:`async_`) entry point
    are exposed so the same fake drives :class:`KeycloakTokenManager` and
    :class:`AsyncKeycloakTokenManager`.

    Attributes:
        requests (List[Dict[str, str]]):
            Every form body passed to the transport, in call order.
        urls (List[str]):
            Every endpoint URL passed to the transport, in call order.
    """

    def __init__(self, responses: List[Dict[str, Any]]) -> None:
        """
        Initialise the fake with the responses to replay.

        Args:
            responses (List[Dict[str, Any]]):
                Scripted JSON token responses, returned one per call in order.
        """
        self._responses = list(responses)
        self.requests: List[Dict[str, str]] = []
        self.urls: List[str] = []

    def _next(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Record one request and return the next scripted response.

        Args:
            url (str):
                The token-endpoint URL the manager called.
            data (Dict[str, str]):
                The form-encoded request body the manager sent.

        Returns:
            Dict[str, Any]:
                The next scripted JSON response.

        Raises:
            AssertionError:
                If no scripted responses remain (the test under-provisioned the fake).
        """
        self.urls.append(url)
        self.requests.append(data)
        if not self._responses:
            raise AssertionError("FakeTransport ran out of scripted responses")
        return self._responses.pop(0)

    def sync(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Synchronous transport entry point for :class:`KeycloakTokenManager`.

        Args:
            url (str):
                The token-endpoint URL.
            data (Dict[str, str]):
                The form-encoded request body.

        Returns:
            Dict[str, Any]:
                The next scripted JSON response.
        """
        return self._next(url, data)

    async def async_(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Asynchronous transport entry point for :class:`AsyncKeycloakTokenManager`.

        Args:
            url (str):
                The token-endpoint URL.
            data (Dict[str, str]):
                The form-encoded request body.

        Returns:
            Dict[str, Any]:
                The next scripted JSON response.
        """
        return self._next(url, data)


def _login_response(access: str = "access-1", refresh: str = "offline-1", expires_in: int = 300) -> Dict[str, Any]:
    """
    Build a scripted Keycloak token-endpoint JSON response.

    Args:
        access (str):
            Value for the ``access_token`` field.
        refresh (str):
            Value for the ``refresh_token`` field.
        expires_in (int):
            Value for the ``expires_in`` field (seconds). Use ``0`` to make the access token
            immediately stale so the next call refreshes.

    Returns:
        Dict[str, Any]:
            A token response dict with ``access_token``/``refresh_token``/``expires_in``/
            ``token_type`` keys.
    """
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }


def _sync_manager(transport: FakeTransport, **overrides: Any) -> KeycloakTokenManager:
    """
    Build a :class:`KeycloakTokenManager` wired to the fake transport with test defaults.

    Args:
        transport (FakeTransport):
            The fake transport whose :meth:`FakeTransport.sync` drives the manager.
        **overrides (Any):
            Constructor keyword overrides (e.g. ``token_expiration_in_s``) applied on top of
            the shared test defaults.

    Returns:
        KeycloakTokenManager:
            A manager configured with the module-level test credentials and the fake
            transport.
    """
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
    """The endpoint builder yields the same URL with or without a trailing slash on the base."""
    assert build_token_endpoint(KEYCLOAK_URL + "/", REALM) == EXPECTED_ENDPOINT
    assert build_token_endpoint(KEYCLOAK_URL, REALM) == EXPECTED_ENDPOINT


def test_manager_exposes_resolved_token_endpoint() -> None:
    """The manager exposes the resolved token endpoint via its ``token_endpoint`` property."""
    transport = FakeTransport([])
    manager = _sync_manager(transport)

    assert manager.token_endpoint == EXPECTED_ENDPOINT


# --------------------------------------------------------------------------------------- #
# Sync manager
# --------------------------------------------------------------------------------------- #
def test_login_uses_ropc_password_grant_with_offline_access_and_no_secret() -> None:
    """Login posts the ROPC password grant with ``offline_access`` and no ``client_secret`` (Q1)."""
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
    """``get_authorization_metadata`` returns the ``("authorization", "Bearer <jwt>")`` tuple."""
    transport = FakeTransport([_login_response(access="jwt-abc")])
    manager = _sync_manager(transport)
    manager.login()

    key, value = manager.get_authorization_metadata()

    assert key == "authorization"
    assert value == "Bearer jwt-abc"


def test_fresh_access_token_is_reused_without_refresh() -> None:
    """A still-fresh access token is returned from cache without hitting the transport again."""
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
    """A stale access token drives a ``grant_type=refresh_token`` exchange with the offline token."""
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
    """``force_refresh=True`` refreshes even when the cached access token is still fresh."""
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
    """When a refresh response omits ``refresh_token`` the previously stored offline token is kept."""
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
    """``token_expiration_in_s=0`` closes the auto-refresh window immediately after login."""
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
    """``token_expiration_in_s=None`` leaves the refresh window open so refreshes keep succeeding."""
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
    """Calling ``get_access_token`` before ``login`` raises a "Not logged in" error."""
    transport = FakeTransport([])
    manager = _sync_manager(transport)

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.get_access_token()

    assert "Not logged in" in str(exc_info.value)


def test_refresh_without_refresh_token_raises() -> None:
    """A refresh with no stored offline token raises before any transport call is made."""
    # A login response that carries an access_token but NO refresh_token, with expires_in=0
    # so the access token is immediately stale: the next get_access_token() drives into
    # _refresh() while the stored refresh_token is still empty, hitting the guard.
    transport = FakeTransport([{"access_token": "jwt-no-refresh", "expires_in": 0}])
    manager = _sync_manager(transport)
    manager.login()

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.get_access_token()

    assert "No refresh token available" in str(exc_info.value)
    # The guard fires before any refresh request is sent (only the login call hit the transport).
    assert len(transport.requests) == 1


def test_login_response_without_access_token_raises() -> None:
    """A login response with no ``access_token`` surfaces the error description in the exception."""
    transport = FakeTransport([{"error": "invalid_grant", "error_description": "bad creds"}])
    manager = _sync_manager(transport)

    with pytest.raises(KeycloakAuthError) as exc_info:
        manager.login()

    assert "bad creds" in str(exc_info.value)


def test_manager_rejects_empty_required_fields() -> None:
    """Constructing a manager with an empty required field raises ``ValueError``."""
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
    """The async manager logs in via the ROPC password grant with ``offline_access`` and no secret."""
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
    """A stale access token in the async manager triggers a refresh-token exchange."""
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
    """``token_expiration_in_s=0`` closes the async refresh window so the next call raises."""
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


@pytest.mark.asyncio
async def test_async_refresh_without_refresh_token_raises() -> None:
    """Async mirror: a refresh with no stored offline token raises before any transport call."""
    # Async mirror of test_refresh_without_refresh_token_raises: login yields an access_token
    # but no refresh_token (expires_in=0 => immediately stale), so get_access_token() drives
    # into _refresh() while the stored refresh_token is empty, hitting the guard.
    transport = FakeTransport([{"access_token": "jwt-no-refresh", "expires_in": 0}])
    manager = AsyncKeycloakTokenManager(
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        transport=transport.async_,
    )

    await manager.login()
    with pytest.raises(KeycloakAuthError) as exc_info:
        await manager.get_access_token()

    assert "No refresh token available" in str(exc_info.value)
    assert len(transport.requests) == 1


# --------------------------------------------------------------------------------------- #
# Default HTTP transports (hermetic: the real requests/aiohttp clients are monkeypatched
# so no network call is made; only the SDK's status-code handling / JSON decoding is run).
# --------------------------------------------------------------------------------------- #
class _FakeRequestsResponse:
    """
    Minimal ``requests.Response`` stand-in for the default sync transport.

    Attributes:
        status_code (int):
            The HTTP status code the fake reports.
        text (str):
            The stringified body (used in the error message on failure).
    """

    def __init__(self, status_code: int, body: Dict[str, Any]) -> None:
        """
        Args:
            status_code (int):
                The HTTP status code to report.
            body (Dict[str, Any]):
                The JSON body returned by :meth:`json` (and stringified into ``text``).
        """
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self) -> Dict[str, Any]:
        """
        Return the decoded JSON body.

        Returns:
            Dict[str, Any]:
                The body passed at construction time.
        """
        return self._body


def test_default_sync_transport_returns_json_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default sync transport posts to the endpoint and returns the decoded JSON on HTTP 200.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to replace ``requests.post`` with a network-free fake.
    """
    import requests

    captured: Dict[str, Any] = {}

    def fake_post(url: str, data: Dict[str, str], timeout: int) -> _FakeRequestsResponse:
        """Capture the call arguments and return a scripted HTTP 200 response."""
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
    """The default sync transport raises ``KeycloakAuthError`` (with the status) on an HTTP >= 400.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to replace ``requests.post`` with a network-free fake.
    """
    import requests

    def fake_post(url: str, data: Dict[str, str], timeout: int) -> _FakeRequestsResponse:
        """Return a scripted HTTP 401 error response."""
        return _FakeRequestsResponse(401, {"error": "invalid_grant"})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(KeycloakAuthError) as exc_info:
        _default_sync_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert "401" in str(exc_info.value)


class _FakeAiohttpResponse:
    """
    Async-context-manager response stand-in for the default async transport.

    Attributes:
        status (int):
            The HTTP status code the fake reports.
    """

    def __init__(self, status: int, body: Dict[str, Any]) -> None:
        """
        Args:
            status (int):
                The HTTP status code to report.
            body (Dict[str, Any]):
                The JSON body returned by :meth:`json` (and stringified by :meth:`text`).
        """
        self.status = status
        self._body = body

    async def __aenter__(self) -> "_FakeAiohttpResponse":
        """Enter the async context, returning this response.

        Returns:
            _FakeAiohttpResponse:
                This response instance.
        """
        return self

    async def __aexit__(self, *exc: Any) -> None:
        """Exit the async context (no-op, never suppresses exceptions).

        Args:
            *exc (Any):
                The ``(type, value, traceback)`` triple supplied by the runtime; ignored.
        """
        return None

    async def json(self) -> Dict[str, Any]:
        """Return the decoded JSON body.

        Returns:
            Dict[str, Any]:
                The body passed at construction time.
        """
        return self._body

    async def text(self) -> str:
        """Return the stringified body (used in the error path).

        Returns:
            str:
                The body rendered with ``str``.
        """
        return str(self._body)


class _FakeAiohttpSession:
    """``aiohttp.ClientSession`` stand-in returning a scripted response."""

    def __init__(self, response: _FakeAiohttpResponse) -> None:
        """
        Args:
            response (_FakeAiohttpResponse):
                The scripted response that :meth:`post` returns.
        """
        self._response = response

    async def __aenter__(self) -> "_FakeAiohttpSession":
        """Enter the async context, returning this session.

        Returns:
            _FakeAiohttpSession:
                This session instance.
        """
        return self

    async def __aexit__(self, *exc: Any) -> None:
        """Exit the async context (no-op, never suppresses exceptions).

        Args:
            *exc (Any):
                The ``(type, value, traceback)`` triple supplied by the runtime; ignored.
        """
        return None

    def post(self, url: str, data: Dict[str, str], timeout: Any) -> _FakeAiohttpResponse:
        """Return the scripted response regardless of the request arguments.

        Args:
            url (str):
                The endpoint URL (ignored by the fake).
            data (Dict[str, str]):
                The form body (ignored by the fake).
            timeout (Any):
                The request timeout (ignored by the fake).

        Returns:
            _FakeAiohttpResponse:
                The scripted response supplied at construction time.
        """
        return self._response


@pytest.mark.asyncio
async def test_default_async_transport_returns_json_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default async transport returns the decoded JSON on an HTTP 200.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to replace ``aiohttp.ClientSession`` with a network-free fake.
    """
    import aiohttp

    response = _FakeAiohttpResponse(200, _login_response(access="jwt-async-default"))
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: _FakeAiohttpSession(response))

    result = await _default_async_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert result["access_token"] == "jwt-async-default"


@pytest.mark.asyncio
async def test_default_async_transport_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default async transport raises ``KeycloakAuthError`` (with the status) on an HTTP >= 400.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to replace ``aiohttp.ClientSession`` with a network-free fake.
    """
    import aiohttp

    response = _FakeAiohttpResponse(500, {"error": "server_error"})
    monkeypatch.setattr(aiohttp, "ClientSession", lambda: _FakeAiohttpSession(response))

    with pytest.raises(KeycloakAuthError) as exc_info:
        await _default_async_transport(EXPECTED_ENDPOINT, {"grant_type": "password"})

    assert "500" in str(exc_info.value)
