from typing import Iterator

from google.protobuf.empty_pb2 import Empty
from ondewo.utils.base_services_interface import BaseServicesInterface

from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
    S2sPipeline,
    S2sPipelineId,
    S2sStreamRequest,
    S2sStreamResponse,
)
from ondewo.csi.conversation_pb2_grpc import ConversationsStub


class Conversations(BaseServicesInterface):
    """
    Exposes the csi endpoints of ONDEWO csi in a user-friendly way.

    See conversation.proto.
    """

    @property
    def stub(self) -> ConversationsStub:
        stub: ConversationsStub = ConversationsStub(channel=self.grpc_channel)
        return stub

    def create_s2s_pipeline(self, request: S2sPipeline) -> Empty:
        response: Empty = self.stub.CreateS2sPipeline(request)
        return response

    def get_s2s_pipeline(self, request: S2sPipelineId) -> S2sPipeline:
        response: S2sPipeline = self.stub.GetS2sPipeline(request)
        return response

    def update_s2s_pipeline(self, request: S2sPipeline) -> Empty:
        response: Empty = self.stub.UpdateS2sPipeline(request)
        return response

    def delete_s2s_pipeline(self, request: S2sPipelineId) -> Empty:
        response: Empty = self.stub.DeleteS2sPipeline(request)
        return response

    def list_s2s_pipelines(self, request: ListS2sPipelinesRequest) -> ListS2sPipelinesResponse:
        response: ListS2sPipelinesResponse = self.stub.ListS2sPipelines(request)
        return response

    def s2s_stream(self, request_iterator: Iterator[S2sStreamRequest]) -> Iterator[S2sStreamResponse]:
        response_iterator: Iterator[S2sStreamResponse] = self.stub.S2sStream(request_iterator)
        return response_iterator
