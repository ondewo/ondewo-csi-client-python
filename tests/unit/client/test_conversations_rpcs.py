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
"""Cover every ``Conversations`` RPC wrapper, sync and async.

Each wrapper is three lines of forwarding -- pick the stub method, attach ``self.metadata``, return
what came back -- and that is exactly where a copy-paste slip hides: a method calling the wrong
stub endpoint, dropping ``metadata`` (so the call goes out unauthenticated), or swallowing the
response. Every RPC is therefore driven through a mock stub and checked on all three counts.

``tests/unit/client/test_conversations_metadata.py`` proves the Keycloak bearer token reaches the
metadata of a call. This module is the breadth complement: the same guarantees across the whole
endpoint surface, so a newly added RPC that forgets ``metadata=self.metadata`` fails here.

No channel is opened and no network call is made -- the stub is replaced with a mock.
"""

from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Tuple,
)
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest
from google.protobuf.empty_pb2 import Empty

from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.core import async_services_interface as async_interface_module
from ondewo.csi.client.core import services_interface as sync_interface_module
from ondewo.csi.client.services.async_conversations import Conversations as AsyncConversations
from ondewo.csi.client.services.conversations import Conversations as SyncConversations
from ondewo.csi.conversation_pb2 import (
    CheckUpstreamHealthResponse,
    ControlStatus,
    ControlStreamRequest,
    ControlStreamResponse,
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
    S2sPipeline,
    S2sPipelineId,
    S2sStreamRequest,
    S2sStreamResponse,
    SetControlStatusRequest,
    SetControlStatusResponse,
)
from ondewo.csi.conversation_pb2_grpc import ConversationsStub

HOST: str = "localhost"
PORT: str = "50055"
PIPELINE_ID: str = "s2s-pipeline-under-test"
TOKEN: str = "header.payload.signature"
BEARER_METADATA: List[Tuple[str, str]] = [("authorization", f"Bearer {TOKEN}")]

#: One entry per unary RPC on the service: (wrapper name, stub endpoint, request, response).
#: The request/response instances are distinctive so "returned the stub's object" cannot be
#: confused with "returned a freshly built empty message of the right type".
UNARY_RPCS: List[Tuple[str, str, Any, Any]] = [
    ("create_s2s_pipeline", "CreateS2sPipeline", S2sPipeline(id=PIPELINE_ID), Empty()),
    ("get_s2s_pipeline", "GetS2sPipeline", S2sPipelineId(id=PIPELINE_ID), S2sPipeline(id=PIPELINE_ID)),
    ("update_s2s_pipeline", "UpdateS2sPipeline", S2sPipeline(id=PIPELINE_ID), Empty()),
    ("delete_s2s_pipeline", "DeleteS2sPipeline", S2sPipelineId(id=PIPELINE_ID), Empty()),
    (
        "list_s2s_pipelines",
        "ListS2sPipelines",
        ListS2sPipelinesRequest(),
        ListS2sPipelinesResponse(pipelines=[S2sPipeline(id=PIPELINE_ID)]),
    ),
    ("check_upstream_health", "CheckUpstreamHealth", Empty(), CheckUpstreamHealthResponse()),
    (
        "set_control_status",
        "SetControlStatus",
        SetControlStatusRequest(control_status=ControlStatus.PLAYBACK_DONE),
        SetControlStatusResponse(),
    ),
]

#: One entry per streaming RPC: (wrapper name, stub endpoint, request factory, response factory).
#: Factories rather than values, because an iterator is single-use -- sharing one across the sync
#: and async parametrizations would leave the second test asserting against a drained stream.
STREAMING_RPCS: List[Tuple[str, str, Callable[[], Any], Callable[[], Any]]] = [
    (
        "get_control_stream",
        "GetControlStream",
        lambda: ControlStreamRequest(),
        lambda: iter([ControlStreamResponse()]),
    ),
    ("s2s_stream", "S2sStream", lambda: iter([S2sStreamRequest()]), lambda: iter([S2sStreamResponse()])),
]


class _FakeProvider:
    """Stand-in `KeycloakTokenProvider` that counts how often a token was demanded."""

    def __init__(self) -> None:
        """Start with no recorded token requests."""
        self.calls: int = 0

    def bearer_metadata(self) -> List[Tuple[str, str]]:
        """Return the canned `Authorization: Bearer` metadata and record the request.

        Returns:
            List[Tuple[str, str]]:
                A fresh copy of the fixed bearer metadata tuple.
        """
        self.calls += 1
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
        keycloak_url="https://kc.example.com/auth",
        realm="ondewo-ccai-platform",
        client_id="ondewo-nlu-cai-sdk-public",
        username="tech-user@example.com",
        password="s3cr3t",
    )


def _anonymous_config() -> ClientConfig:
    """Build an unauthenticated client config (no Keycloak fields).

    Returns:
        ClientConfig:
            A config whose `keycloak_configured` is `False`.
    """
    return ClientConfig(host=HOST, port=PORT)


def _sync_service(monkeypatch: pytest.MonkeyPatch) -> Tuple[SyncConversations, MagicMock, _FakeProvider]:
    """Build a sync `Conversations` with a fake token provider and a mock stub.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the token-provider factory and the service stub.

    Returns:
        Tuple[SyncConversations, MagicMock, _FakeProvider]:
            The service, its mock stub, and the provider handing out bearer metadata.
    """
    provider: _FakeProvider = _FakeProvider()
    monkeypatch.setattr(sync_interface_module, "get_keycloak_token_provider", lambda config: provider)

    service: SyncConversations = SyncConversations(config=_keycloak_config(), use_secure_channel=False)
    stub: MagicMock = MagicMock()
    monkeypatch.setattr(type(service), "stub", property(lambda self: stub))
    return service, stub, provider


def _async_service(monkeypatch: pytest.MonkeyPatch) -> Tuple[AsyncConversations, MagicMock, _FakeProvider]:
    """Build an async `Conversations` with a fake token provider and a mock stub.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the token-provider factory and the service stub.

    Returns:
        Tuple[AsyncConversations, MagicMock, _FakeProvider]:
            The service, its mock stub, and the provider handing out bearer metadata.
    """
    provider: _FakeProvider = _FakeProvider()
    monkeypatch.setattr(async_interface_module, "get_keycloak_token_provider", lambda config: provider)

    service: AsyncConversations = AsyncConversations(config=_keycloak_config(), use_secure_channel=False)
    stub: MagicMock = MagicMock()
    monkeypatch.setattr(type(service), "stub", property(lambda self: stub))
    return service, stub, provider


# region sync RPC surface


@pytest.mark.parametrize(("wrapper", "endpoint", "request_message", "response_message"), UNARY_RPCS)
def test_sync_unary_rpc_forwards_request_metadata_and_response(
    monkeypatch: pytest.MonkeyPatch,
    wrapper: str,
    endpoint: str,
    request_message: Any,
    response_message: Any,
) -> None:
    """Each sync unary wrapper calls its own endpoint with metadata and returns the response.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
        wrapper (str):
            Name of the method on `Conversations` under test.
        endpoint (str):
            Name of the gRPC stub method it must call.
        request_message (Any):
            The request handed to the wrapper.
        response_message (Any):
            The response the stub is primed to return.
    """
    service, stub, _ = _sync_service(monkeypatch)
    getattr(stub, endpoint).return_value = response_message

    result: Any = getattr(service, wrapper)(request_message)

    getattr(stub, endpoint).assert_called_once_with(request_message, metadata=BEARER_METADATA)
    # Identity, not equality: a wrapper returning a fresh empty message would still compare equal.
    assert result is response_message


@pytest.mark.parametrize(("wrapper", "endpoint", "make_request", "make_response"), STREAMING_RPCS)
def test_sync_streaming_rpc_returns_the_iterator_unconsumed(
    monkeypatch: pytest.MonkeyPatch,
    wrapper: str,
    endpoint: str,
    make_request: Callable[[], Any],
    make_response: Callable[[], Any],
) -> None:
    """Each sync streaming wrapper hands back the stub's iterator without draining it.

    Materializing the stream inside the wrapper would break the streaming contract and buffer an
    unbounded response, so the returned object must be the stub's own iterator.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
        wrapper (str):
            Name of the method on `Conversations` under test.
        endpoint (str):
            Name of the gRPC stub method it must call.
        make_request (Callable[[], Any]):
            Builds the request (or request iterator) handed to the wrapper.
        make_response (Callable[[], Any]):
            Builds the response iterator the stub is primed to return.
    """
    service, stub, _ = _sync_service(monkeypatch)
    request_message: Any = make_request()
    response_message: Any = make_response()
    getattr(stub, endpoint).return_value = response_message

    result: Any = getattr(service, wrapper)(request_message)

    getattr(stub, endpoint).assert_called_once_with(request_message, metadata=BEARER_METADATA)
    assert result is response_message
    # Still full: the wrapper must not have pulled an item off the stream.
    assert len(list(result)) == 1


def test_sync_s2s_stream_does_not_consume_the_request_iterator(monkeypatch: pytest.MonkeyPatch) -> None:
    """`s2s_stream` forwards the request iterator lazily, without pulling from it.

    A bidirectional stream is fed by a live generator (microphone frames, in the examples).
    Consuming it in the wrapper -- or turning it into a list -- would block until the caller stopped
    speaking, so the generator must still be untouched after the call returns.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
    """
    service, stub, _ = _sync_service(monkeypatch)
    stub.S2sStream.return_value = iter([S2sStreamResponse()])

    consumed: List[int] = []

    def _requests() -> Iterator[S2sStreamRequest]:
        """Yield one request, recording that the generator was advanced.

        Yields:
            S2sStreamRequest:
                A single empty stream request.
        """
        consumed.append(1)
        yield S2sStreamRequest()

    request_iterator: Iterator[S2sStreamRequest] = _requests()
    service.s2s_stream(request_iterator)

    assert consumed == []
    stub.S2sStream.assert_called_once_with(request_iterator, metadata=BEARER_METADATA)


def test_sync_metadata_is_rebuilt_for_every_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every RPC re-reads the token provider, so an expiring token is refreshed between calls.

    Caching `metadata` once on the service would keep sending the first access token until it
    expired mid-session -- the whole point of the auto-refreshing provider.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
    """
    service, stub, provider = _sync_service(monkeypatch)
    stub.ListS2sPipelines.return_value = ListS2sPipelinesResponse()

    service.list_s2s_pipelines(ListS2sPipelinesRequest())
    service.list_s2s_pipelines(ListS2sPipelinesRequest())

    assert provider.calls == 2


def test_sync_anonymous_service_sends_no_auth_metadata_on_any_rpc(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without Keycloak the wrappers still call the stub, with empty metadata.

    csi has no legacy `cai-token` fallback, so an unauthenticated client must send an empty list --
    not `None`, which gRPC would reject.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the service stub.
    """
    service: SyncConversations = SyncConversations(config=_anonymous_config(), use_secure_channel=False)
    stub: MagicMock = MagicMock()
    monkeypatch.setattr(type(service), "stub", property(lambda self: stub))

    request: S2sPipelineId = S2sPipelineId(id=PIPELINE_ID)
    stub.DeleteS2sPipeline.return_value = Empty()
    service.delete_s2s_pipeline(request)

    stub.DeleteS2sPipeline.assert_called_once_with(request, metadata=[])


def test_sync_stub_property_binds_the_service_channel() -> None:
    """The real `stub` property builds a `ConversationsStub` on the service's own channel.

    Every wrapper reads `self.stub`, so this is the one line all of them depend on.
    """
    service: SyncConversations = SyncConversations(config=_anonymous_config(), use_secure_channel=False)

    stub: ConversationsStub = service.stub

    assert isinstance(stub, ConversationsStub)
    # A fresh stub per access: the property constructs rather than caching.
    assert service.stub is not stub


# endregion sync RPC surface

# region async RPC surface


@pytest.mark.asyncio
@pytest.mark.parametrize(("wrapper", "endpoint", "request_message", "response_message"), UNARY_RPCS)
async def test_async_unary_rpc_forwards_request_metadata_and_response(
    monkeypatch: pytest.MonkeyPatch,
    wrapper: str,
    endpoint: str,
    request_message: Any,
    response_message: Any,
) -> None:
    """Each async unary wrapper awaits its own endpoint with metadata and returns the response.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
        wrapper (str):
            Name of the method on `Conversations` under test.
        endpoint (str):
            Name of the gRPC stub method it must await.
        request_message (Any):
            The request handed to the wrapper.
        response_message (Any):
            The response the stub is primed to return.
    """
    service, stub, _ = _async_service(monkeypatch)
    setattr(stub, endpoint, AsyncMock(return_value=response_message))

    result: Any = await getattr(service, wrapper)(request_message)

    getattr(stub, endpoint).assert_awaited_once_with(request_message, metadata=BEARER_METADATA)
    assert result is response_message


@pytest.mark.asyncio
@pytest.mark.parametrize(("wrapper", "endpoint", "make_request", "make_response"), STREAMING_RPCS)
async def test_async_streaming_rpc_returns_the_iterator_unconsumed(
    monkeypatch: pytest.MonkeyPatch,
    wrapper: str,
    endpoint: str,
    make_request: Callable[[], Any],
    make_response: Callable[[], Any],
) -> None:
    """Each async streaming wrapper hands back the stub's iterator without draining it.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
        wrapper (str):
            Name of the method on `Conversations` under test.
        endpoint (str):
            Name of the gRPC stub method it must await.
        make_request (Callable[[], Any]):
            Builds the request (or request iterator) handed to the wrapper.
        make_response (Callable[[], Any]):
            Builds the response iterator the stub is primed to return.
    """
    service, stub, _ = _async_service(monkeypatch)
    request_message: Any = make_request()
    response_message: Any = make_response()
    setattr(stub, endpoint, AsyncMock(return_value=response_message))

    result: Any = await getattr(service, wrapper)(request_message)

    getattr(stub, endpoint).assert_awaited_once_with(request_message, metadata=BEARER_METADATA)
    assert result is response_message
    assert len(list(result)) == 1


@pytest.mark.asyncio
async def test_async_metadata_is_rebuilt_for_every_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every async RPC re-reads the token provider, so an expiring token is refreshed between calls.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to build the service against a mock stub.
    """
    service, stub, provider = _async_service(monkeypatch)
    stub.ListS2sPipelines = AsyncMock(return_value=ListS2sPipelinesResponse())

    await service.list_s2s_pipelines(ListS2sPipelinesRequest())
    await service.list_s2s_pipelines(ListS2sPipelinesRequest())

    assert provider.calls == 2


@pytest.mark.asyncio
async def test_async_anonymous_service_sends_no_auth_metadata_on_any_rpc(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without Keycloak the async wrappers still call the stub, with empty metadata.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to swap the service stub.
    """
    service: AsyncConversations = AsyncConversations(config=_anonymous_config(), use_secure_channel=False)
    stub: MagicMock = MagicMock()
    monkeypatch.setattr(type(service), "stub", property(lambda self: stub))

    request: S2sPipelineId = S2sPipelineId(id=PIPELINE_ID)
    stub.DeleteS2sPipeline = AsyncMock(return_value=Empty())
    await service.delete_s2s_pipeline(request)

    stub.DeleteS2sPipeline.assert_awaited_once_with(request, metadata=[])


@pytest.mark.asyncio
async def test_async_stub_property_binds_the_service_channel() -> None:
    """The real async `stub` property builds a `ConversationsStub` on the service's own channel."""
    service: AsyncConversations = AsyncConversations(config=_anonymous_config(), use_secure_channel=False)

    stub: ConversationsStub = service.stub

    assert isinstance(stub, ConversationsStub)
    assert service.stub is not stub


# endregion async RPC surface
