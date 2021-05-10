# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ondewo.csi import conversation_pb2 as ondewo_dot_csi_dot_conversation__pb2


class ConversationsStub(object):
    """endpoints of csi service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateS2sPipeline = channel.unary_unary(
                '/ondewo.csi.Conversations/CreateS2sPipeline',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.GetS2sPipeline = channel.unary_unary(
                '/ondewo.csi.Conversations/GetS2sPipeline',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.SerializeToString,
                response_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.FromString,
                )
        self.UpdateS2sPipeline = channel.unary_unary(
                '/ondewo.csi.Conversations/UpdateS2sPipeline',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.DeleteS2sPipeline = channel.unary_unary(
                '/ondewo.csi.Conversations/DeleteS2sPipeline',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.ListS2sPipelines = channel.unary_unary(
                '/ondewo.csi.Conversations/ListS2sPipelines',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesRequest.SerializeToString,
                response_deserializer=ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesResponse.FromString,
                )
        self.S2sStream = channel.stream_stream(
                '/ondewo.csi.Conversations/S2sStream',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sStreamRequest.SerializeToString,
                response_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sStreamResponse.FromString,
                )
        self.CheckHealth = channel.unary_unary(
                '/ondewo.csi.Conversations/CheckHealth',
                request_serializer=ondewo_dot_csi_dot_conversation__pb2.CheckHealthRequest.SerializeToString,
                response_deserializer=ondewo_dot_csi_dot_conversation__pb2.CheckHealthResponse.FromString,
                )


class ConversationsServicer(object):
    """endpoints of csi service
    """

    def CreateS2sPipeline(self, request, context):
        """Create the S2S pipeline specified in the request message. The pipeline with the specified ID must not exist.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetS2sPipeline(self, request, context):
        """Retrieve the S2S pipeline with the ID specified in the request message.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateS2sPipeline(self, request, context):
        """Update the S2S pipeline specified in the request message. The pipeline must exist.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteS2sPipeline(self, request, context):
        """Delete the S2S pipeline with the ID specified in the request message. The pipeline must exist.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListS2sPipelines(self, request, context):
        """List all S2S pipelines of the server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def S2sStream(self, request_iterator, context):
        """Processes a natural language query in audio format in a streaming fashion
        and returns structured, actionable data as a result.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckHealth(self, request, context):
        """Check the health of S2T, NLU and T2S servers
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConversationsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateS2sPipeline': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateS2sPipeline,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'GetS2sPipeline': grpc.unary_unary_rpc_method_handler(
                    servicer.GetS2sPipeline,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.FromString,
                    response_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.SerializeToString,
            ),
            'UpdateS2sPipeline': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateS2sPipeline,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'DeleteS2sPipeline': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteS2sPipeline,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'ListS2sPipelines': grpc.unary_unary_rpc_method_handler(
                    servicer.ListS2sPipelines,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesRequest.FromString,
                    response_serializer=ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesResponse.SerializeToString,
            ),
            'S2sStream': grpc.stream_stream_rpc_method_handler(
                    servicer.S2sStream,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.S2sStreamRequest.FromString,
                    response_serializer=ondewo_dot_csi_dot_conversation__pb2.S2sStreamResponse.SerializeToString,
            ),
            'CheckHealth': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckHealth,
                    request_deserializer=ondewo_dot_csi_dot_conversation__pb2.CheckHealthRequest.FromString,
                    response_serializer=ondewo_dot_csi_dot_conversation__pb2.CheckHealthResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ondewo.csi.Conversations', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Conversations(object):
    """endpoints of csi service
    """

    @staticmethod
    def CreateS2sPipeline(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/CreateS2sPipeline',
            ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetS2sPipeline(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/GetS2sPipeline',
            ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.SerializeToString,
            ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateS2sPipeline(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/UpdateS2sPipeline',
            ondewo_dot_csi_dot_conversation__pb2.S2sPipeline.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteS2sPipeline(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/DeleteS2sPipeline',
            ondewo_dot_csi_dot_conversation__pb2.S2sPipelineId.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListS2sPipelines(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/ListS2sPipelines',
            ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesRequest.SerializeToString,
            ondewo_dot_csi_dot_conversation__pb2.ListS2sPipelinesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def S2sStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/ondewo.csi.Conversations/S2sStream',
            ondewo_dot_csi_dot_conversation__pb2.S2sStreamRequest.SerializeToString,
            ondewo_dot_csi_dot_conversation__pb2.S2sStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CheckHealth(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ondewo.csi.Conversations/CheckHealth',
            ondewo_dot_csi_dot_conversation__pb2.CheckHealthRequest.SerializeToString,
            ondewo_dot_csi_dot_conversation__pb2.CheckHealthResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
