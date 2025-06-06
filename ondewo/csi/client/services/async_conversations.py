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
from typing import Iterator

from google.protobuf.empty_pb2 import Empty
from ondewo.utils.async_base_services_interface import AsyncBaseServicesInterface

from ondewo.csi.conversation_pb2 import (
    CheckUpstreamHealthResponse,
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


class Conversations(AsyncBaseServicesInterface):
    """
    Exposes the csi endpoints of ONDEWO csi in a user-friendly way.

    See conversation.proto.
    """

    @property
    def stub(self) -> ConversationsStub:
        stub: ConversationsStub = ConversationsStub(channel=self.grpc_channel)
        return stub

    async def create_s2s_pipeline(self, request: S2sPipeline) -> Empty:
        response: Empty = await self.stub.CreateS2sPipeline(request)
        return response

    async def get_s2s_pipeline(self, request: S2sPipelineId) -> S2sPipeline:
        response: S2sPipeline = await self.stub.GetS2sPipeline(request)
        return response

    async def update_s2s_pipeline(self, request: S2sPipeline) -> Empty:
        response: Empty = await self.stub.UpdateS2sPipeline(request)
        return response

    async def delete_s2s_pipeline(self, request: S2sPipelineId) -> Empty:
        response: Empty = await self.stub.DeleteS2sPipeline(request)
        return response

    async def list_s2s_pipelines(self, request: ListS2sPipelinesRequest) -> ListS2sPipelinesResponse:
        response: ListS2sPipelinesResponse = await self.stub.ListS2sPipelines(request)
        return response

    async def s2s_stream(self, request_iterator: Iterator[S2sStreamRequest]) -> Iterator[S2sStreamResponse]:
        response_iterator: Iterator[S2sStreamResponse] = await self.stub.S2sStream(request_iterator)
        return response_iterator

    async def check_upstream_health(self, request: Empty) -> CheckUpstreamHealthResponse:
        response: CheckUpstreamHealthResponse = await self.stub.CheckUpstreamHealth(request)
        return response

    async def get_control_stream(self, request: ControlStreamRequest) -> Iterator[ControlStreamResponse]:
        response_iterator: Iterator[ControlStreamResponse] = await self.stub.GetControlStream(request)
        return response_iterator

    async def set_control_status(self, request: SetControlStatusRequest) -> SetControlStatusResponse:
        response: SetControlStatusResponse = await self.stub.SetControlStatus(request)
        return response
