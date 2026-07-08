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
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
from ondewo.utils.base_client_config import BaseClientConfig


@dataclass_json
@dataclass(frozen=True)
class ClientConfig(BaseClientConfig):
    """
    Configuration for the ONDEWO CSI client.

    This class extends ``BaseClientConfig`` (``host``/``port``/``grpc_cert``) with the
    Keycloak headless-authentication fields used by the D18 offline-token flow.

    The client authenticates against a **public** Keycloak client (no ``client_secret``,
    Q1) using the Resource-Owner-Password-Credentials (ROPC) grant with
    ``scope=offline_access``, then auto-refreshes the short-lived access token and sends
    it as ``Authorization: Bearer <jwt>`` (D5 — the legacy ``cai-token`` / HTTP-Basic
    ``http_token`` are gone).

    All fields are optional and default to empty so pre-existing JSON configs (which only
    carry ``host``/``port``/``grpc_cert``) keep loading unchanged. Keycloak authentication
    is only attempted when ``keycloak_url`` (and the rest of the Keycloak fields) are set.

    Attributes:
        keycloak_url (str):
            Base URL of the Keycloak server, e.g. ``"https://keycloak.ondewo.com/auth"``.
        realm (str):
            Keycloak realm that owns the SDK client and the user, e.g.
            ``"ondewo-ccai-platform"``.
        client_id (str):
            The **public** Keycloak client id used for the ROPC grant, e.g.
            ``"ondewo-nlu-cai-sdk-public"``. No ``client_secret`` is used (Q1).
        username (str):
            Username (email) of the 2FA-exempt technical user. The legacy ``user_name``
            field is accepted as an alias and kept working for ROPC.
        user_name (str):
            Legacy alias for ``username`` (kept for backward compatibility). If both are
            set, ``username`` wins.
        password (str):
            Password of the technical user.
        token_expiration_in_s (Optional[int]):
            Optional upper bound (in seconds, since login) on how long the background
            auto-refresh keeps renewing the access token. Once elapsed the refresh loop
            stops and subsequent calls fail until a fresh login. ``None`` ⇒ refresh until
            the Keycloak offline session itself expires.
        keycloak_verify_ssl (bool):
            Whether to verify the Keycloak server's TLS certificate on the token-endpoint
            call. Defaults to ``True`` (secure). Set ``False`` only for a self-signed/local
            Envoy at ``https://localhost:12001/auth``.
    """

    keycloak_url: str = ""
    realm: str = ""
    client_id: str = ""
    username: str = ""
    user_name: str = ""
    password: str = ""
    token_expiration_in_s: Optional[int] = None
    keycloak_verify_ssl: bool = True

    def __post_init__(self) -> None:
        """
        Validate the Keycloak fields without requiring the removed ``http_token``.

        ``http_token`` (HTTP Basic) is no longer part of the contract (D5) and is **not**
        required. Validation is intentionally lenient: a config with no Keycloak fields is
        valid (anonymous / no-auth, as before). As soon as any Keycloak field is supplied
        the whole set plus credentials must be present, so partial misconfiguration fails
        fast instead of silently sending unauthenticated calls.

        Raises:
            ValueError:
                If only some of the Keycloak authentication fields are provided.
        """
        super(ClientConfig, self).__post_init__()

        keycloak_fields = {
            "keycloak_url": self.keycloak_url,
            "realm": self.realm,
            "client_id": self.client_id,
            "password": self.password,
        }
        provided = {name for name, value in keycloak_fields.items() if value}
        # The resolved username may come from either `username` or the legacy `user_name`.
        if self.resolved_username:
            provided.add("username")

        if provided and provided != {"keycloak_url", "realm", "client_id", "username", "password"}:
            missing = sorted({"keycloak_url", "realm", "client_id", "username", "password"} - provided)
            raise ValueError(
                f"Incomplete Keycloak configuration in {self.__class__.__name__}: "
                f"missing field(s) {missing}. Provide all of keycloak_url, realm, client_id, "
                "username (or user_name), password — or none of them for an unauthenticated client."
            )

    @property
    def resolved_username(self) -> str:
        """
        Resolve the effective username, preferring ``username`` over legacy ``user_name``.

        Returns:
            str:
                ``username`` if set, otherwise ``user_name`` (legacy alias), otherwise "".
        """
        return self.username or self.user_name

    @property
    def keycloak_configured(self) -> bool:
        """
        Whether this config carries a complete Keycloak headless-auth configuration.

        Returns:
            bool:
                ``True`` when ``keycloak_url``/``realm``/``client_id``/username/password are
                all present, so the D18 offline-token flow can run.
        """
        return bool(self.keycloak_url and self.realm and self.client_id and self.resolved_username and self.password)
