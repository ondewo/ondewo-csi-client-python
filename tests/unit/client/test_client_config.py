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
"""Hermetic unit tests for the D18 Keycloak fields on the CSI ``ClientConfig``."""

from typing import (
    Any,
    Dict,
)

import pytest

from ondewo.csi.client.client_config import ClientConfig

KEYCLOAK_URL = "https://keycloak.ondewo.com/auth"
REALM = "ondewo-ccai-platform"
CLIENT_ID = "ondewo-nlu-cai-sdk-public"
USERNAME = "tech-user@ondewo.com"
PASSWORD = "s3cret"


def _full_keycloak_config(**overrides: Any) -> ClientConfig:
    """
    Build a fully-configured Keycloak :class:`ClientConfig` with test defaults.

    Args:
        **overrides (Any):
            Constructor keyword overrides applied on top of the complete default set (e.g.
            ``user_name`` to test the legacy alias).

    Returns:
        ClientConfig:
            A config with host/port plus all five Keycloak fields populated.
    """
    kwargs: Dict[str, Any] = {
        "host": "localhost",
        "port": "50055",
        "keycloak_url": KEYCLOAK_URL,
        "realm": REALM,
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
    }
    kwargs.update(overrides)
    return ClientConfig(**kwargs)


def test_legacy_host_port_only_config_still_loads() -> None:
    """A pre-D18 host/port-only JSON config still parses and reports no Keycloak configuration."""
    # Backward compatibility: a pre-D18 JSON config with only host/port (no http_token,
    # no keycloak fields) must keep parsing — http_token is no longer required.
    config = ClientConfig.from_json('{"host": "localhost", "port": "50055"}')

    assert config.host == "localhost"
    assert config.port == "50055"
    assert config.keycloak_configured is False
    assert config.resolved_username == ""


def test_http_token_is_not_required_and_not_a_field() -> None:
    """The removed ``http_token`` is no longer a constructor field, so passing it raises (D5)."""
    # The removed http_token must not be a constructor field anymore (D5).
    with pytest.raises(TypeError):
        ClientConfig(host="localhost", port="50055", http_token="basic")  # type: ignore[call-arg]


def test_full_keycloak_config_parses_from_json() -> None:
    """A full Keycloak JSON config parses, reports configured, and resolves the username/expiry."""
    raw = (
        '{"host": "localhost", "port": "50055",'
        f' "keycloak_url": "{KEYCLOAK_URL}", "realm": "{REALM}",'
        f' "client_id": "{CLIENT_ID}", "username": "{USERNAME}",'
        f' "password": "{PASSWORD}", "token_expiration_in_s": 3600}}'
    )
    config = ClientConfig.from_json(raw)

    assert config.keycloak_configured is True
    assert config.resolved_username == USERNAME
    assert config.token_expiration_in_s == 3600


def test_no_client_secret_field_exists() -> None:
    """The public SDK client config exposes no ``client_secret`` attribute (Q1)."""
    # Q1: the SDK client is PUBLIC — there must be no client_secret field.
    config = _full_keycloak_config()
    assert not hasattr(config, "client_secret")


def test_legacy_user_name_alias_drives_ropc() -> None:
    """The legacy ``user_name`` field is accepted as the username alias and satisfies the config."""
    # "keep user_name/password ROPC working": user_name is accepted as the username alias.
    config = ClientConfig(
        host="localhost",
        port="50055",
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        user_name=USERNAME,
        password=PASSWORD,
    )

    assert config.resolved_username == USERNAME
    assert config.keycloak_configured is True


def test_username_wins_over_legacy_user_name() -> None:
    """When both are set, ``username`` takes precedence over the legacy ``user_name`` alias."""
    config = _full_keycloak_config(user_name="legacy@ondewo.com")
    assert config.resolved_username == USERNAME


def test_partial_keycloak_config_raises() -> None:
    """A partial Keycloak config (url only, no credentials) fails fast with a descriptive error."""
    # keycloak_url present but credentials missing -> fail fast, do not silently send
    # unauthenticated calls.
    with pytest.raises(ValueError) as exc_info:
        ClientConfig(host="localhost", port="50055", keycloak_url=KEYCLOAK_URL)

    message = str(exc_info.value)
    assert "Incomplete Keycloak configuration" in message
    assert "realm" in message
    assert "client_id" in message


def test_missing_password_only_raises() -> None:
    """An otherwise-complete Keycloak config missing only ``password`` raises naming the field."""
    with pytest.raises(ValueError) as exc_info:
        ClientConfig(
            host="localhost",
            port="50055",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
        )
    assert "password" in str(exc_info.value)
