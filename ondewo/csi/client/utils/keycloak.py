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
Headless Keycloak authentication for the ONDEWO CSI Python SDK (migration-plan D18).

The SDK authenticates against a **public** Keycloak client (no ``client_secret``, Q1)
with the Resource-Owner-Password-Credentials (ROPC, ``grant_type=password``) grant and
``scope=offline_access``. The initial login returns a short-lived access token and a
long-lived offline refresh token; the access token is then auto-refreshed
(``grant_type=refresh_token``) and attached to every gRPC call as
``Authorization: Bearer <jwt>`` (D5 — the legacy ``cai-token`` / HTTP-Basic header are
gone).

``token_expiration_in_s`` (optional) bounds how long the auto-refresh keeps running: once
that many seconds have elapsed since login, the manager stops issuing refreshes (further
calls fail until a fresh login), capping the lifetime of a long-lived headless session.

Both a synchronous (:class:`KeycloakTokenManager`, ``requests``) and an asynchronous
(:class:`AsyncKeycloakTokenManager`, ``aiohttp``) manager are provided. The HTTP transport
is injectable so the managers can be unit-tested fully offline (no network).
"""
import logging
import time
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Tuple,
)

logger = logging.getLogger(__name__)

# gRPC metadata key for the bearer token. Lower-case per the HTTP/2 + gRPC metadata spec
# (metadata keys are case-insensitive but conventionally lower-case).
AUTHORIZATION_METADATA_KEY = "authorization"

# Refresh the access token this many seconds *before* it actually expires, so the hot path
# never races the expiry boundary.
_EXPIRY_SKEW_S = 30

# A token request that does not declare its lifetime is treated as already-stale so the
# next call refreshes rather than sending a possibly-expired token.
_DEFAULT_EXPIRES_IN_S = 0

# Response of the Keycloak token endpoint, decoded from JSON.
TokenResponse = Dict[str, Any]

# A synchronous HTTP transport: (url, form-encoded data) -> decoded JSON token response.
SyncTransport = Callable[[str, Dict[str, str]], TokenResponse]

# An asynchronous HTTP transport: (url, form-encoded data) -> awaitable JSON token response.
AsyncTransport = Callable[[str, Dict[str, str]], Awaitable[TokenResponse]]


class KeycloakAuthError(Exception):
    """Raised when Keycloak authentication or token refresh fails."""


def build_token_endpoint(keycloak_url: str, realm: str) -> str:
    """
    Build the Keycloak OpenID-Connect token endpoint URL.

    Args:
        keycloak_url (str):
            Base Keycloak URL, e.g. ``"https://keycloak.ondewo.com/auth"``. A trailing
            slash is tolerated.
        realm (str):
            Realm name, e.g. ``"ondewo-ccai-platform"``.

    Returns:
        str:
            ``<keycloak_url>/realms/<realm>/protocol/openid-connect/token``.
    """
    base = keycloak_url.rstrip("/")
    return f"{base}/realms/{realm}/protocol/openid-connect/token"


@dataclass
class _TokenState:
    """Mutable token state shared by the sync and async managers."""

    access_token: str = ""
    refresh_token: str = ""
    # Monotonic deadline (``time.monotonic`` seconds) after which the access token is stale.
    access_token_deadline: float = 0.0
    # Monotonic deadline after which auto-refresh stops (``token_expiration_in_s`` bound).
    # ``None`` ⇒ no bound (refresh until the offline session itself expires).
    refresh_deadline: Optional[float] = None
    logged_in: bool = field(default=False)

    def store(self, response: TokenResponse) -> None:
        """
        Persist a token response and recompute the access-token refresh deadline.

        Args:
            response (TokenResponse):
                Decoded Keycloak token-endpoint JSON. Must contain ``access_token``; a
                missing ``refresh_token`` keeps the previously stored one (Keycloak omits
                it on some refreshes).

        Raises:
            KeycloakAuthError:
                If the response carries no ``access_token``.
        """
        access_token = response.get("access_token")
        if not access_token:
            error = response.get("error_description") or response.get("error") or "no access_token in response"
            raise KeycloakAuthError(f"Keycloak token response did not contain an access_token: {error}")

        self.access_token = access_token
        # Keycloak omits refresh_token on some refresh responses; keep the existing offline token.
        refresh_token = response.get("refresh_token")
        if refresh_token:
            self.refresh_token = refresh_token

        expires_in = int(response.get("expires_in", _DEFAULT_EXPIRES_IN_S))
        self.access_token_deadline = time.monotonic() + max(expires_in - _EXPIRY_SKEW_S, 0)

    def access_token_fresh(self) -> bool:
        """Whether the stored access token is still within its (skewed) validity window."""
        return bool(self.access_token) and time.monotonic() < self.access_token_deadline

    def refresh_window_open(self) -> bool:
        """Whether ``token_expiration_in_s`` still permits another refresh."""
        if self.refresh_deadline is None:
            return True
        return time.monotonic() < self.refresh_deadline


def _password_grant_data(client_id: str, username: str, password: str) -> Dict[str, str]:
    """Build the ROPC ``grant_type=password`` form body with ``scope=offline_access``."""
    return {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password,
        "scope": "offline_access",
    }


def _refresh_grant_data(client_id: str, refresh_token: str) -> Dict[str, str]:
    """Build the ``grant_type=refresh_token`` form body for the offline-token exchange."""
    return {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token,
    }


class _KeycloakManagerBase:
    """Shared configuration and bookkeeping for the sync and async token managers."""

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
    ) -> None:
        if not (keycloak_url and realm and client_id and username and password):
            raise ValueError(
                "KeycloakTokenManager requires non-empty keycloak_url, realm, client_id, username and password."
            )
        self._client_id = client_id
        self._username = username
        self._password = password
        self._token_expiration_in_s = token_expiration_in_s
        self._token_endpoint = build_token_endpoint(keycloak_url=keycloak_url, realm=realm)
        self._state = _TokenState()

    @property
    def token_endpoint(self) -> str:
        """The resolved Keycloak token endpoint URL."""
        return self._token_endpoint

    def _on_login(self, response: TokenResponse) -> None:
        """Record the login response, the login instant and the auto-refresh deadline."""
        self._state.store(response)
        self._state.logged_in = True
        if self._token_expiration_in_s is not None:
            self._state.refresh_deadline = time.monotonic() + self._token_expiration_in_s

    def _require_logged_in(self) -> None:
        if not self._state.logged_in:
            raise KeycloakAuthError("Not logged in: call login() before requesting authorization metadata.")

    def _require_refresh_window(self) -> None:
        if not self._state.refresh_window_open():
            raise KeycloakAuthError(
                "token_expiration_in_s elapsed: the auto-refresh window is closed, a fresh login() is required."
            )

    @staticmethod
    def _bearer_metadata(access_token: str) -> Tuple[str, str]:
        """Build the ``Authorization: Bearer`` gRPC metadata tuple."""
        return (AUTHORIZATION_METADATA_KEY, f"Bearer {access_token}")


class KeycloakTokenManager(_KeycloakManagerBase):
    """
    Synchronous headless Keycloak token manager (ROPC offline token + auto-refresh).

    Usage::

        manager = KeycloakTokenManager(
            keycloak_url="https://keycloak.ondewo.com/auth",
            realm="ondewo-ccai-platform",
            client_id="ondewo-nlu-cai-sdk-public",
            username="tech-user@ondewo.com",
            password="…",
            token_expiration_in_s=3600,
        )
        manager.login()
        metadata = [manager.get_authorization_metadata()]  # ("authorization", "Bearer …")
    """

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[SyncTransport] = None,
    ) -> None:
        """
        Args:
            keycloak_url (str):
                Base Keycloak URL (e.g. ``"https://keycloak.ondewo.com/auth"``).
            realm (str):
                Realm name.
            client_id (str):
                Public ROPC client id (no secret, Q1).
            username (str):
                Technical-user username/email.
            password (str):
                Technical-user password.
            token_expiration_in_s (Optional[int]):
                Upper bound on the auto-refresh lifetime (see module docstring).
            transport (Optional[SyncTransport]):
                Injectable HTTP transport ``(url, data) -> dict`` for hermetic testing. If
                omitted, a ``requests``-backed transport is used.
        """
        super().__init__(
            keycloak_url=keycloak_url,
            realm=realm,
            client_id=client_id,
            username=username,
            password=password,
            token_expiration_in_s=token_expiration_in_s,
        )
        self._transport: SyncTransport = transport or _default_sync_transport

    def login(self) -> None:
        """
        Perform the one-time ROPC + ``offline_access`` login.

        Raises:
            KeycloakAuthError:
                If the token endpoint rejects the credentials or returns no access token.
        """
        data = _password_grant_data(self._client_id, self._username, self._password)
        logger.debug("Keycloak ROPC login for client_id=%s user=%s", self._client_id, self._username)
        response = self._transport(self._token_endpoint, data)
        self._on_login(response)

    def _refresh(self) -> None:
        """Exchange the offline refresh token for a fresh access token."""
        if not self._state.refresh_token:
            raise KeycloakAuthError("No refresh token available: login() must succeed first.")
        data = _refresh_grant_data(self._client_id, self._state.refresh_token)
        logger.debug("Keycloak token refresh for client_id=%s", self._client_id)
        response = self._transport(self._token_endpoint, data)
        self._state.store(response)

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Return a valid access token, refreshing from the offline token when needed.

        Args:
            force_refresh (bool):
                Refresh even if the cached access token still looks fresh (used to replay a
                call that failed with ``UNAUTHENTICATED``).

        Returns:
            str:
                A current access token.

        Raises:
            KeycloakAuthError:
                If not logged in, if the ``token_expiration_in_s`` window has closed, or if
                the refresh fails.
        """
        self._require_logged_in()
        if self._state.access_token_fresh() and not force_refresh:
            return self._state.access_token
        self._require_refresh_window()
        self._refresh()
        return self._state.access_token

    def get_authorization_metadata(self, force_refresh: bool = False) -> Tuple[str, str]:
        """
        Return the ``("authorization", "Bearer <jwt>")`` gRPC metadata tuple.

        Args:
            force_refresh (bool):
                Force a token refresh before building the metadata.

        Returns:
            Tuple[str, str]:
                The bearer-token metadata tuple ready to pass to a gRPC call.
        """
        return self._bearer_metadata(self.get_access_token(force_refresh=force_refresh))


class AsyncKeycloakTokenManager(_KeycloakManagerBase):
    """Asynchronous counterpart of :class:`KeycloakTokenManager` (``aiohttp`` transport)."""

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[AsyncTransport] = None,
    ) -> None:
        """See :class:`KeycloakTokenManager`; ``transport`` is an async callable here."""
        super().__init__(
            keycloak_url=keycloak_url,
            realm=realm,
            client_id=client_id,
            username=username,
            password=password,
            token_expiration_in_s=token_expiration_in_s,
        )
        self._transport: AsyncTransport = transport or _default_async_transport

    async def login(self) -> None:
        """Perform the one-time ROPC + ``offline_access`` login. See sync ``login``."""
        data = _password_grant_data(self._client_id, self._username, self._password)
        logger.debug("Keycloak ROPC login for client_id=%s user=%s", self._client_id, self._username)
        response = await self._transport(self._token_endpoint, data)
        self._on_login(response)

    async def _refresh(self) -> None:
        """Exchange the offline refresh token for a fresh access token."""
        if not self._state.refresh_token:
            raise KeycloakAuthError("No refresh token available: login() must succeed first.")
        data = _refresh_grant_data(self._client_id, self._state.refresh_token)
        logger.debug("Keycloak token refresh for client_id=%s", self._client_id)
        response = await self._transport(self._token_endpoint, data)
        self._state.store(response)

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Return a valid access token, refreshing when needed. See sync ``get_access_token``."""
        self._require_logged_in()
        if self._state.access_token_fresh() and not force_refresh:
            return self._state.access_token
        self._require_refresh_window()
        await self._refresh()
        return self._state.access_token

    async def get_authorization_metadata(self, force_refresh: bool = False) -> Tuple[str, str]:
        """Return the ``("authorization", "Bearer <jwt>")`` gRPC metadata tuple."""
        access_token = await self.get_access_token(force_refresh=force_refresh)
        return self._bearer_metadata(access_token)


def _default_sync_transport(url: str, data: Dict[str, str]) -> TokenResponse:
    """Default ``requests``-backed POST to the Keycloak token endpoint."""
    import requests

    response = requests.post(url, data=data, timeout=30)
    if response.status_code >= 400:
        raise KeycloakAuthError(
            f"Keycloak token endpoint returned HTTP {response.status_code}: {response.text}"
        )
    result: TokenResponse = response.json()
    return result


async def _default_async_transport(url: str, data: Dict[str, str]) -> TokenResponse:
    """Default ``aiohttp``-backed POST to the Keycloak token endpoint."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status >= 400:
                body = await response.text()
                raise KeycloakAuthError(
                    f"Keycloak token endpoint returned HTTP {response.status}: {body}"
                )
            result: TokenResponse = await response.json()
            return result
