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
"""Cover the two client entry points and the service containers they populate.

``BaseClient.__init__`` raises ``ValueError`` unless ``_initialize_services`` assigns
``self.services``, so simply constructing a client already proves the override ran and wired a
``Conversations`` service. These tests go further and pin down what the container holds, that the
channel-security choice reaches the service, and that per-client gRPC ``options`` are forwarded
rather than dropped.

No network traffic happens: ``use_secure_channel=False`` yields a lazily-connecting
``grpc.insecure_channel`` and no RPC is issued.
"""

from typing import (
    Any,
    Dict,
    List,
    Set,
    Tuple,
)
from unittest.mock import MagicMock

import pytest
from ondewo.utils import async_base_services_interface as async_base_module
from ondewo.utils import base_services_interface as sync_base_module

from ondewo.csi.client.async_client import AsyncClient
from ondewo.csi.client.async_services_container import AsyncServicesContainer
from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.async_conversations import Conversations as AsyncConversations
from ondewo.csi.client.services.conversations import Conversations as SyncConversations
from ondewo.csi.client.services_container import ServicesContainer

HOST: str = "localhost"
PORT: str = "50055"
#: A non-default channel option value, chosen so the assertion cannot pass against the shared defaults.
OPTION_KEY: str = "grpc.max_receive_message_length"
OPTION_VALUE: int = 1234
CHANNEL_OPTIONS: Set[Tuple[str, Any]] = {(OPTION_KEY, OPTION_VALUE)}
#: A secret that must never surface in an error message rendered from a config.
PLANTED_PASSWORD: str = "s3cr3t-in-error-path"


def _config() -> ClientConfig:
    """Build a minimal unauthenticated client config.

    Returns:
        ClientConfig:
            A config carrying only host and port, so no Keycloak login is attempted.
    """
    return ClientConfig(host=HOST, port=PORT)


def _capture_channel_options(monkeypatch: pytest.MonkeyPatch, module: Any) -> List[Dict[str, Any]]:
    """Replace a base module's channel factory with a recorder.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the module-level ``_get_grpc_channel``.
        module (Any):
            The ``ondewo.utils`` base module whose factory should be recorded.

    Returns:
        List[Dict[str, Any]]:
            A list, appended to once per constructed service, holding the options actually passed.
    """
    recorded: List[Dict[str, Any]] = []

    def _fake_get_grpc_channel(config: Any, use_secure_channel: bool, options: Any) -> MagicMock:
        recorded.append(dict(options))
        return MagicMock()

    monkeypatch.setattr(module, "_get_grpc_channel", _fake_get_grpc_channel)
    return recorded


def test_client_initializes_conversations_service() -> None:
    """`Client` populates `services` with a `ServicesContainer` holding a `Conversations`."""
    client: Client = Client(config=_config(), use_secure_channel=False)

    assert isinstance(client.services, ServicesContainer)
    assert isinstance(client.services.conversations, SyncConversations)
    # An open channel is what makes the service usable; a container of `None` would still be truthy.
    assert client.services.conversations.grpc_channel is not None


def test_client_forwards_channel_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """`Client` passes per-client gRPC options through to the channel, overriding the default.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to record the options handed to the channel factory.
    """
    recorded: List[Dict[str, Any]] = _capture_channel_options(monkeypatch, sync_base_module)

    Client(config=_config(), use_secure_channel=False, options=CHANNEL_OPTIONS)

    assert len(recorded) == 1
    # The override wins over the shared default, and the untouched defaults survive the merge.
    assert recorded[0][OPTION_KEY] == OPTION_VALUE
    assert recorded[0]["grpc.enable_retries"] == 1


def test_client_without_options_uses_the_shared_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Omitting `options` leaves the default channel options untouched.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to record the options handed to the channel factory.
    """
    recorded: List[Dict[str, Any]] = _capture_channel_options(monkeypatch, sync_base_module)

    Client(config=_config(), use_secure_channel=False)

    assert len(recorded) == 1
    assert recorded[0][OPTION_KEY] != OPTION_VALUE


def test_client_without_certificate_rejects_secure_channel() -> None:
    """A secure channel with no `grpc_cert` fails loudly instead of silently going insecure."""
    with pytest.raises(ValueError):
        Client(config=_config(), use_secure_channel=True)


def test_client_secure_channel_error_does_not_leak_the_password() -> None:
    """The `ValueError` renders the config through the redacting `__repr__`, not the raw fields.

    The message interpolates the whole config, so it inherits `ClientConfig.__repr__`. The guard
    is that this error path cannot become a second place where credentials reach a log.
    """
    config: ClientConfig = ClientConfig(
        host=HOST,
        port=PORT,
        keycloak_url="https://kc.example.com/auth",
        realm="ondewo-ccai-platform",
        client_id="ondewo-nlu-cai-sdk-public",
        username="tech-user@example.com",
        password=PLANTED_PASSWORD,
    )
    # Assert the secret is really on the object first, so the absence check below cannot pass vacuously.
    assert config.password == PLANTED_PASSWORD

    with pytest.raises(ValueError) as excinfo:
        Client(config=config, use_secure_channel=True)

    assert PLANTED_PASSWORD not in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_client_initializes_conversations_service() -> None:
    """`AsyncClient` populates `services` with an `AsyncServicesContainer` holding a `Conversations`."""
    client: AsyncClient = AsyncClient(config=_config(), use_secure_channel=False)

    assert isinstance(client.services, AsyncServicesContainer)
    assert isinstance(client.services.conversations, AsyncConversations)
    assert client.services.conversations.grpc_channel is not None


@pytest.mark.asyncio
async def test_async_client_forwards_channel_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """`AsyncClient` passes per-client gRPC options through to the channel, overriding the default.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to record the options handed to the async channel factory.
    """
    recorded: List[Dict[str, Any]] = _capture_channel_options(monkeypatch, async_base_module)

    AsyncClient(config=_config(), use_secure_channel=False, options=CHANNEL_OPTIONS)

    assert len(recorded) == 1
    assert recorded[0][OPTION_KEY] == OPTION_VALUE
    assert recorded[0]["grpc.enable_retries"] == 1


@pytest.mark.asyncio
async def test_async_client_without_certificate_rejects_secure_channel() -> None:
    """A secure async channel with no `grpc_cert` fails loudly instead of silently going insecure."""
    with pytest.raises(ValueError):
        AsyncClient(config=_config(), use_secure_channel=True)


def test_sync_and_async_containers_are_distinct_types() -> None:
    """The sync and async containers are separate types, so an import mix-up cannot hide.

    Both wrap a class literally named `Conversations`; importing the wrong one in
    `_initialize_services` would otherwise be invisible at runtime.
    """
    assert ServicesContainer is not AsyncServicesContainer
    assert SyncConversations is not AsyncConversations
