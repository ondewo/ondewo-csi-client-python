# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
)

from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer as google___protobuf___internal___containers___RepeatedCompositeFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from ondewo.nlu.session_pb2 import (
    DetectIntentResponse as ondewo___nlu___session_pb2___DetectIntentResponse,
)

from ondewo.t2s.text_to_speech_pb2 import (
    SynthesizeResponse as ondewo___t2s___text_to_speech_pb2___SynthesizeResponse,
)

from typing import (
    Iterable as typing___Iterable,
    Optional as typing___Optional,
    Text as typing___Text,
    Union as typing___Union,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int
if sys.version_info < (3,):
    builtin___buffer = buffer
    builtin___unicode = unicode


class S2sPipeline(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    id = ... # type: typing___Text
    s2t_pipeline_id = ... # type: typing___Text
    nlu_project_id = ... # type: typing___Text
    nlu_language_code = ... # type: typing___Text
    t2s_pipeline_id = ... # type: typing___Text

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        s2t_pipeline_id : typing___Optional[typing___Text] = None,
        nlu_project_id : typing___Optional[typing___Text] = None,
        nlu_language_code : typing___Optional[typing___Text] = None,
        t2s_pipeline_id : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> S2sPipeline: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> S2sPipeline: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id",u"nlu_language_code",b"nlu_language_code",u"nlu_project_id",b"nlu_project_id",u"s2t_pipeline_id",b"s2t_pipeline_id",u"t2s_pipeline_id",b"t2s_pipeline_id"]) -> None: ...
global___S2sPipeline = S2sPipeline

class S2sPipelineId(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    id = ... # type: typing___Text

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> S2sPipelineId: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> S2sPipelineId: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id"]) -> None: ...
global___S2sPipelineId = S2sPipelineId

class ListS2sPipelinesRequest(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> ListS2sPipelinesRequest: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> ListS2sPipelinesRequest: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
global___ListS2sPipelinesRequest = ListS2sPipelinesRequest

class ListS2sPipelinesResponse(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def pipelines(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[global___S2sPipeline]: ...

    def __init__(self,
        *,
        pipelines : typing___Optional[typing___Iterable[global___S2sPipeline]] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> ListS2sPipelinesResponse: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> ListS2sPipelinesResponse: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"pipelines",b"pipelines"]) -> None: ...
global___ListS2sPipelinesResponse = ListS2sPipelinesResponse

class S2sStreamRequest(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    pipeline_id = ... # type: typing___Text
    session_id = ... # type: typing___Text
    audio = ... # type: builtin___bytes
    end_of_stream = ... # type: builtin___bool
    initial_intent_display_name = ... # type: typing___Text

    def __init__(self,
        *,
        pipeline_id : typing___Optional[typing___Text] = None,
        session_id : typing___Optional[typing___Text] = None,
        audio : typing___Optional[builtin___bytes] = None,
        end_of_stream : typing___Optional[builtin___bool] = None,
        initial_intent_display_name : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> S2sStreamRequest: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> S2sStreamRequest: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"audio",b"audio",u"end_of_stream",b"end_of_stream",u"initial_intent_display_name",b"initial_intent_display_name",u"pipeline_id",b"pipeline_id",u"session_id",b"session_id"]) -> None: ...
global___S2sStreamRequest = S2sStreamRequest

class S2sStreamResponse(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def detect_intent_response(self) -> ondewo___nlu___session_pb2___DetectIntentResponse: ...

    @property
    def synthetize_response(self) -> ondewo___t2s___text_to_speech_pb2___SynthesizeResponse: ...

    def __init__(self,
        *,
        detect_intent_response : typing___Optional[ondewo___nlu___session_pb2___DetectIntentResponse] = None,
        synthetize_response : typing___Optional[ondewo___t2s___text_to_speech_pb2___SynthesizeResponse] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> S2sStreamResponse: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> S2sStreamResponse: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"detect_intent_response",b"detect_intent_response",u"response",b"response",u"synthetize_response",b"synthetize_response"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"detect_intent_response",b"detect_intent_response",u"response",b"response",u"synthetize_response",b"synthetize_response"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions___Literal[u"response",b"response"]) -> typing_extensions___Literal["detect_intent_response","synthetize_response"]: ...
global___S2sStreamResponse = S2sStreamResponse
