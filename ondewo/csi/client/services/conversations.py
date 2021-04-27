from typing import Iterator

from ondewo.utils.base_services_interface import BaseServicesInterface

from ondewo.csi.conversation_pb2 import S2sStreamRequest, S2sStreamResponse
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

    def s2s_stream(self, request_iterator: Iterator[S2sStreamRequest]) -> Iterator[S2sStreamResponse]:
        response_iterator: Iterator[S2sStreamResponse] = self.stub.S2sStream(request_iterator)
        return response_iterator
