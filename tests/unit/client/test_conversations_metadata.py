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
"""Prove the Keycloak bearer token actually reaches an outgoing stub call.

These tests exercise the real ``Conversations`` service (sync + async) rather than a mocked
client, so they catch the regression where the provider was wired but never invoked on the
RPC path. No channel is opened and no Keycloak/network call is made: the stub is replaced
with a mock and the token provider is swapped for a fake that yields a known bearer tuple.
"""
from typing import (
    List,
    Tuple,
)
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.core import async_services_interface as async_interface_module
from ondewo.csi.client.core import services_interface as sync_interface_module
from ondewo.csi.client.services.async_conversations import Conversations as AsyncConversations
from ondewo.csi.client.services.conversations import Conversations as SyncConversations
from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
)

# Bound exactly once so a refactor that changes only an input or only an expectation cannot
# silently make a test tautological.
HOST: str = 'localhost'
PORT: str = '50055'
KEYCLOAK_URL: str = 'https://kc.example.com/auth'
REALM: str = 'ondewo-ccai-platform'
CLIENT_ID: str = 'ondewo-nlu-cai-sdk-public'
USERNAME: str = 'tech-user@example.com'
PASSWORD: str = 's3cr3t'
TOKEN: str = 'header.payload.signature'
BEARER_METADATA: List[Tuple[str, str]] = [('authorization', f'Bearer {TOKEN}')]


class _FakeProvider:
    """Stand-in `KeycloakTokenProvider` that yields a fixed bearer metadata list."""

    def bearer_metadata(self) -> List[Tuple[str, str]]:
        """Return the canned `Authorization: Bearer` metadata.

        Returns:
            List[Tuple[str, str]]:
                A copy of the fixed bearer metadata tuple.
        """
        return list(BEARER_METADATA)


def _keycloak_config() -> ClientConfig:
    """Build a complete Keycloak-configured client config.

    Returns:
        ClientConfig:
            A config whose `keycloak_configured` is `True`.
    """
    return ClientConfig(
        host=HOST,
        port=PORT,
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
    )


def _anonymous_config() -> ClientConfig:
    """Build an unauthenticated client config (no Keycloak fields).

    Returns:
        ClientConfig:
            A config whose `keycloak_configured` is `False`.
    """
    return ClientConfig(host=HOST, port=PORT)


def test_sync_conversations_attaches_bearer_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """A Keycloak-configured sync `Conversations` forwards the bearer token as call metadata.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the token-provider factory and the service stub.
    """
    monkeypatch.setattr(sync_interface_module, 'get_keycloak_token_provider', lambda config: _FakeProvider())

    conversations: SyncConversations = SyncConversations(config=_keycloak_config(), use_secure_channel=False)

    stub: MagicMock = MagicMock()
    stub.ListS2sPipelines.return_value = ListS2sPipelinesResponse()
    monkeypatch.setattr(type(conversations), 'stub', property(lambda self: stub))

    request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    conversations.list_s2s_pipelines(request)

    stub.ListS2sPipelines.assert_called_once_with(request, metadata=BEARER_METADATA)


def test_sync_conversations_anonymous_sends_empty_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unauthenticated sync `Conversations` sends empty metadata (no legacy fallback).

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the service stub.
    """
    conversations: SyncConversations = SyncConversations(config=_anonymous_config(), use_secure_channel=False)
    assert conversations.metadata == []

    stub: MagicMock = MagicMock()
    stub.ListS2sPipelines.return_value = ListS2sPipelinesResponse()
    monkeypatch.setattr(type(conversations), 'stub', property(lambda self: stub))

    request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    conversations.list_s2s_pipelines(request)

    stub.ListS2sPipelines.assert_called_once_with(request, metadata=[])


@pytest.mark.asyncio
async def test_async_conversations_attaches_bearer_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """A Keycloak-configured async `Conversations` forwards the bearer token as call metadata.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the token-provider factory and the service stub.
    """
    monkeypatch.setattr(async_interface_module, 'get_keycloak_token_provider', lambda config: _FakeProvider())

    conversations: AsyncConversations = AsyncConversations(config=_keycloak_config(), use_secure_channel=False)

    stub: MagicMock = MagicMock()
    stub.ListS2sPipelines = AsyncMock(return_value=ListS2sPipelinesResponse())
    monkeypatch.setattr(type(conversations), 'stub', property(lambda self: stub))

    request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    await conversations.list_s2s_pipelines(request)

    stub.ListS2sPipelines.assert_awaited_once_with(request, metadata=BEARER_METADATA)


@pytest.mark.asyncio
async def test_async_conversations_anonymous_sends_empty_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unauthenticated async `Conversations` sends empty metadata (no legacy fallback).

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the service stub.
    """
    conversations: AsyncConversations = AsyncConversations(config=_anonymous_config(), use_secure_channel=False)
    assert conversations.metadata == []

    stub: MagicMock = MagicMock()
    stub.ListS2sPipelines = AsyncMock(return_value=ListS2sPipelinesResponse())
    monkeypatch.setattr(type(conversations), 'stub', property(lambda self: stub))

    request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    await conversations.list_s2s_pipelines(request)

    stub.ListS2sPipelines.assert_awaited_once_with(request, metadata=[])
