"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.struct_pb2
import google.protobuf.timestamp_pb2
import google.rpc.status_pb2
import ondewo.nlu.session_pb2
import ondewo.s2t.speech_to_text_pb2
import ondewo.t2s.text_to_speech_pb2
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor = ...

class ControlStatus(_ControlStatus, metaclass=_ControlStatusEnumTypeWrapper):
    pass
class _ControlStatus:
    V = typing.NewType('V', builtins.int)
class _ControlStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ControlStatus.V], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
    OK = ControlStatus.V(0)
    EMERGENCY_STOP = ControlStatus.V(1)

OK = ControlStatus.V(0)
EMERGENCY_STOP = ControlStatus.V(1)
global___ControlStatus = ControlStatus


class ControlMessageServiceName(_ControlMessageServiceName, metaclass=_ControlMessageServiceNameEnumTypeWrapper):
    pass
class _ControlMessageServiceName:
    V = typing.NewType('V', builtins.int)
class _ControlMessageServiceNameEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ControlMessageServiceName.V], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
    UNKNOWNNAME = ControlMessageServiceName.V(0)
    ondewo_s2t = ControlMessageServiceName.V(1)
    ondewo_t2s = ControlMessageServiceName.V(2)
    ondewo_nlu = ControlMessageServiceName.V(3)

UNKNOWNNAME = ControlMessageServiceName.V(0)
ondewo_s2t = ControlMessageServiceName.V(1)
ondewo_t2s = ControlMessageServiceName.V(2)
ondewo_nlu = ControlMessageServiceName.V(3)
global___ControlMessageServiceName = ControlMessageServiceName


class ControlMessageServiceMethod(_ControlMessageServiceMethod, metaclass=_ControlMessageServiceMethodEnumTypeWrapper):
    pass
class _ControlMessageServiceMethod:
    V = typing.NewType('V', builtins.int)
class _ControlMessageServiceMethodEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ControlMessageServiceMethod.V], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
    UNKNOWNMETHOD = ControlMessageServiceMethod.V(0)
    update_config = ControlMessageServiceMethod.V(1)
    undo_config = ControlMessageServiceMethod.V(2)
    reset_config = ControlMessageServiceMethod.V(3)

UNKNOWNMETHOD = ControlMessageServiceMethod.V(0)
update_config = ControlMessageServiceMethod.V(1)
undo_config = ControlMessageServiceMethod.V(2)
reset_config = ControlMessageServiceMethod.V(3)
global___ControlMessageServiceMethod = ControlMessageServiceMethod


class S2sPipeline(google.protobuf.message.Message):
    """The top-level message sent by client to `CreateS2sPipeline` and `UpdateS2sPipeline` endpoints and received from
    `GetS2sPipeline` endpoint.
    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    ID_FIELD_NUMBER: builtins.int
    S2T_PIPELINE_ID_FIELD_NUMBER: builtins.int
    NLU_PROJECT_ID_FIELD_NUMBER: builtins.int
    NLU_LANGUAGE_CODE_FIELD_NUMBER: builtins.int
    T2S_PIPELINE_ID_FIELD_NUMBER: builtins.int
    id: typing.Text = ...
    """Required. CSI pipeline identifier consisting of S2T, NLU and T2S configuration. ID can be any non-empty string."""

    s2t_pipeline_id: typing.Text = ...
    """Required. S2T pipeline ID, e.g. "german_general" """

    nlu_project_id: typing.Text = ...
    """Required. NLU project ID, usually a hash, e.g. "ae33586b-afda-494a-aa73-1af0589cfc56"."""

    nlu_language_code: typing.Text = ...
    """Required. Language code present in the corresponding NLU project, e.g. "de"."""

    t2s_pipeline_id: typing.Text = ...
    """Required. T2S pipeline ID, e.g. "kerstin"."""

    def __init__(self,
        *,
        id : typing.Text = ...,
        s2t_pipeline_id : typing.Text = ...,
        nlu_project_id : typing.Text = ...,
        nlu_language_code : typing.Text = ...,
        t2s_pipeline_id : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id",b"id","nlu_language_code",b"nlu_language_code","nlu_project_id",b"nlu_project_id","s2t_pipeline_id",b"s2t_pipeline_id","t2s_pipeline_id",b"t2s_pipeline_id"]) -> None: ...
global___S2sPipeline = S2sPipeline

class S2sPipelineId(google.protobuf.message.Message):
    """The top-level message sent by client to `GetS2sPipeline` and `DeleteS2sPipeline` endpoints."""
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    ID_FIELD_NUMBER: builtins.int
    id: typing.Text = ...
    """Required. CSI pipeline identifier."""

    def __init__(self,
        *,
        id : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id",b"id"]) -> None: ...
global___S2sPipelineId = S2sPipelineId

class ListS2sPipelinesRequest(google.protobuf.message.Message):
    """The top-level message sent by client to `ListS2sPipelines` endpoint. Currently without arguments.
    TODO: add filtering options
    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    def __init__(self,
        ) -> None: ...
global___ListS2sPipelinesRequest = ListS2sPipelinesRequest

class ListS2sPipelinesResponse(google.protobuf.message.Message):
    """The top-level message received from `ListS2sPipelines` endpoint."""
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    PIPELINES_FIELD_NUMBER: builtins.int
    @property
    def pipelines(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___S2sPipeline]:
        """Collection of S2S pipelines of the server."""
        pass
    def __init__(self,
        *,
        pipelines : typing.Optional[typing.Iterable[global___S2sPipeline]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["pipelines",b"pipelines"]) -> None: ...
global___ListS2sPipelinesResponse = ListS2sPipelinesResponse

class S2sStreamRequest(google.protobuf.message.Message):
    """The top-level message sent by the client to the
    `S2sStream` method.

    Multiple request messages should be sent in order:

    1.  The first message must contain `pipeline_id` and can contain `session_id` or `initial_intent_display_name`.
        The message must not contain `audio` nor `end_of_stream`.

    2.  All subsequent messages must contain `audio`. If `end_of_stream` is `true`, the stream is closed.
    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    PIPELINE_ID_FIELD_NUMBER: builtins.int
    SESSION_ID_FIELD_NUMBER: builtins.int
    AUDIO_FIELD_NUMBER: builtins.int
    END_OF_STREAM_FIELD_NUMBER: builtins.int
    INITIAL_INTENT_DISPLAY_NAME_FIELD_NUMBER: builtins.int
    pipeline_id: typing.Text = ...
    """Optional. The CSI pipeline ID specified in the initial request."""

    session_id: typing.Text = ...
    """Optional. The session or call ID specified in the initial request. It’s up to the API caller to choose
    an appropriate string. It can be a random number or some type of user identifier (preferably hashed).
    """

    audio: builtins.bytes = ...
    """Optional. The input audio content to be recognized."""

    end_of_stream: builtins.bool = ...
    """If `true`, the recognizer will not return
    any further hypotheses about this piece of the audio. May only be populated
    for `event_type` = `RECOGNITION_EVENT_TRANSCRIPT`.
    """

    initial_intent_display_name: typing.Text = ...
    """Optional. Intent display name to trigger in NLU system in the beginning of the conversation."""

    def __init__(self,
        *,
        pipeline_id : typing.Text = ...,
        session_id : typing.Text = ...,
        audio : builtins.bytes = ...,
        end_of_stream : builtins.bool = ...,
        initial_intent_display_name : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["audio",b"audio","end_of_stream",b"end_of_stream","initial_intent_display_name",b"initial_intent_display_name","pipeline_id",b"pipeline_id","session_id",b"session_id"]) -> None: ...
global___S2sStreamRequest = S2sStreamRequest

class S2sStreamResponse(google.protobuf.message.Message):
    """The top-level message returned from the
    `S2sStream` method.

    A response message is returned for each utterance of the input stream. It contains the full response from NLU system
    in `detect_intent_response` or the full T2S response in `synthetize_response`.
    Multiple response messages can be returned in order:

    1.  The first response message for an input utterance contains response from NLU system `detect_intent_response`
        with detected intent and N fulfillment messages (N >= 0).

    2.  The next N response messages contain for each fulfillment message one of the following:
         a. T2S response `synthetize_response` with synthetized audio
         b. SIP trigger message `sip_trigger` with SIP trigger extracted from the fulfillment message
    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    DETECT_INTENT_RESPONSE_FIELD_NUMBER: builtins.int
    SYNTHETIZE_RESPONSE_FIELD_NUMBER: builtins.int
    SIP_TRIGGER_FIELD_NUMBER: builtins.int
    @property
    def detect_intent_response(self) -> ondewo.nlu.session_pb2.DetectIntentResponse:
        """full NLU response"""
        pass
    @property
    def synthetize_response(self) -> ondewo.t2s.text_to_speech_pb2.SynthesizeResponse:
        """full T2S response"""
        pass
    @property
    def sip_trigger(self) -> global___SipTrigger:
        """SIP trigger message"""
        pass
    def __init__(self,
        *,
        detect_intent_response : typing.Optional[ondewo.nlu.session_pb2.DetectIntentResponse] = ...,
        synthetize_response : typing.Optional[ondewo.t2s.text_to_speech_pb2.SynthesizeResponse] = ...,
        sip_trigger : typing.Optional[global___SipTrigger] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["detect_intent_response",b"detect_intent_response","response",b"response","sip_trigger",b"sip_trigger","synthetize_response",b"synthetize_response"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["detect_intent_response",b"detect_intent_response","response",b"response","sip_trigger",b"sip_trigger","synthetize_response",b"synthetize_response"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["response",b"response"]) -> typing.Optional[typing_extensions.Literal["detect_intent_response","synthetize_response","sip_trigger"]]: ...
global___S2sStreamResponse = S2sStreamResponse

class SipTrigger(google.protobuf.message.Message):
    """SIP trigger message"""
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class SipTriggerType(_SipTriggerType, metaclass=_SipTriggerTypeEnumTypeWrapper):
        """type of the SIP trigger"""
        pass
    class _SipTriggerType:
        V = typing.NewType('V', builtins.int)
    class _SipTriggerTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_SipTriggerType.V], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
        UNSPECIFIED = SipTrigger.SipTriggerType.V(0)
        """should never be used"""

        HANGUP = SipTrigger.SipTriggerType.V(1)
        """hard hangup"""

        HUMAN_HANDOVER = SipTrigger.SipTriggerType.V(2)
        """handover to human"""

        SEND_NOW = SipTrigger.SipTriggerType.V(3)
        """send now"""

        PAUSE = SipTrigger.SipTriggerType.V(4)
        """pause"""


    UNSPECIFIED = SipTrigger.SipTriggerType.V(0)
    """should never be used"""

    HANGUP = SipTrigger.SipTriggerType.V(1)
    """hard hangup"""

    HUMAN_HANDOVER = SipTrigger.SipTriggerType.V(2)
    """handover to human"""

    SEND_NOW = SipTrigger.SipTriggerType.V(3)
    """send now"""

    PAUSE = SipTrigger.SipTriggerType.V(4)
    """pause"""


    TYPE_FIELD_NUMBER: builtins.int
    CONTENT_FIELD_NUMBER: builtins.int
    type: global___SipTrigger.SipTriggerType.V = ...
    @property
    def content(self) -> google.protobuf.struct_pb2.Struct:
        """extra parameters for the trigger"""
        pass
    def __init__(self,
        *,
        type : global___SipTrigger.SipTriggerType.V = ...,
        content : typing.Optional[google.protobuf.struct_pb2.Struct] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["content",b"content"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["content",b"content","type",b"type"]) -> None: ...
global___SipTrigger = SipTrigger

class CheckUpstreamHealthResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    S2T_STATUS_FIELD_NUMBER: builtins.int
    NLU_STATUS_FIELD_NUMBER: builtins.int
    T2S_STATUS_FIELD_NUMBER: builtins.int
    @property
    def s2t_status(self) -> google.rpc.status_pb2.Status: ...
    @property
    def nlu_status(self) -> google.rpc.status_pb2.Status: ...
    @property
    def t2s_status(self) -> google.rpc.status_pb2.Status: ...
    def __init__(self,
        *,
        s2t_status : typing.Optional[google.rpc.status_pb2.Status] = ...,
        nlu_status : typing.Optional[google.rpc.status_pb2.Status] = ...,
        t2s_status : typing.Optional[google.rpc.status_pb2.Status] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["nlu_status",b"nlu_status","s2t_status",b"s2t_status","t2s_status",b"t2s_status"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["nlu_status",b"nlu_status","s2t_status",b"s2t_status","t2s_status",b"t2s_status"]) -> None: ...
global___CheckUpstreamHealthResponse = CheckUpstreamHealthResponse

class ControlStreamRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    def __init__(self,
        ) -> None: ...
global___ControlStreamRequest = ControlStreamRequest

class ControlStreamResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    CONTROL_STATUS_FIELD_NUMBER: builtins.int
    control_status: global___ControlStatus.V = ...
    def __init__(self,
        *,
        control_status : global___ControlStatus.V = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["control_status",b"control_status"]) -> None: ...
global___ControlStreamResponse = ControlStreamResponse

class SetControlStatusRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    CONTROL_STATUS_FIELD_NUMBER: builtins.int
    control_status: global___ControlStatus.V = ...
    def __init__(self,
        *,
        control_status : global___ControlStatus.V = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["control_status",b"control_status"]) -> None: ...
global___SetControlStatusRequest = SetControlStatusRequest

class SetControlStatusResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    OLD_CONTROL_STATUS_FIELD_NUMBER: builtins.int
    NEW_CONTROL_STATUS_FIELD_NUMBER: builtins.int
    old_control_status: global___ControlStatus.V = ...
    new_control_status: global___ControlStatus.V = ...
    def __init__(self,
        *,
        old_control_status : global___ControlStatus.V = ...,
        new_control_status : global___ControlStatus.V = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["new_control_status",b"new_control_status","old_control_status",b"old_control_status"]) -> None: ...
global___SetControlStatusResponse = SetControlStatusResponse

class CondtionValueUnion(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    INT_VALUE_FIELD_NUMBER: builtins.int
    FLOAT_VALUE_FIELD_NUMBER: builtins.int
    DATETIME_VALUE_FIELD_NUMBER: builtins.int
    int_value: builtins.int = ...
    float_value: builtins.float = ...
    @property
    def datetime_value(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(self,
        *,
        int_value : builtins.int = ...,
        float_value : builtins.float = ...,
        datetime_value : typing.Optional[google.protobuf.timestamp_pb2.Timestamp] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["UnionOneof",b"UnionOneof","datetime_value",b"datetime_value","float_value",b"float_value","int_value",b"int_value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["UnionOneof",b"UnionOneof","datetime_value",b"datetime_value","float_value",b"float_value","int_value",b"int_value"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["UnionOneof",b"UnionOneof"]) -> typing.Optional[typing_extensions.Literal["int_value","float_value","datetime_value"]]: ...
global___CondtionValueUnion = CondtionValueUnion

class Condition(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    TYPE_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    type: typing.Text = ...
    @property
    def value(self) -> global___CondtionValueUnion: ...
    def __init__(self,
        *,
        type : typing.Text = ...,
        value : typing.Optional[global___CondtionValueUnion] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["type",b"type","value",b"value"]) -> None: ...
global___Condition = Condition

class ControlMessageServiceParameters(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class ConditionStartEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text = ...
        @property
        def value(self) -> global___Condition: ...
        def __init__(self,
            *,
            key : typing.Text = ...,
            value : typing.Optional[global___Condition] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    class ConditionEndEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text = ...
        @property
        def value(self) -> global___Condition: ...
        def __init__(self,
            *,
            key : typing.Text = ...,
            value : typing.Optional[global___Condition] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    T2S_CONFIG_FIELD_NUMBER: builtins.int
    S2T_CONFIG_FIELD_NUMBER: builtins.int
    CONDITION_START_FIELD_NUMBER: builtins.int
    CONDITION_END_FIELD_NUMBER: builtins.int
    @property
    def t2s_config(self) -> ondewo.t2s.text_to_speech_pb2.RequestConfig: ...
    @property
    def s2t_config(self) -> ondewo.s2t.speech_to_text_pb2.TranscribeRequestConfig: ...
    @property
    def condition_start(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___Condition]: ...
    @property
    def condition_end(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___Condition]: ...
    def __init__(self,
        *,
        t2s_config : typing.Optional[ondewo.t2s.text_to_speech_pb2.RequestConfig] = ...,
        s2t_config : typing.Optional[ondewo.s2t.speech_to_text_pb2.TranscribeRequestConfig] = ...,
        condition_start : typing.Optional[typing.Mapping[typing.Text, global___Condition]] = ...,
        condition_end : typing.Optional[typing.Mapping[typing.Text, global___Condition]] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["config",b"config","s2t_config",b"s2t_config","t2s_config",b"t2s_config"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["condition_end",b"condition_end","condition_start",b"condition_start","config",b"config","s2t_config",b"s2t_config","t2s_config",b"t2s_config"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["config",b"config"]) -> typing.Optional[typing_extensions.Literal["t2s_config","s2t_config"]]: ...
global___ControlMessageServiceParameters = ControlMessageServiceParameters

class ControlMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    SERVICE_FIELD_NUMBER: builtins.int
    METHOD_FIELD_NUMBER: builtins.int
    PARAMETERS_FIELD_NUMBER: builtins.int
    service: global___ControlMessageServiceName.V = ...
    method: global___ControlMessageServiceMethod.V = ...
    @property
    def parameters(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ControlMessageServiceParameters]: ...
    def __init__(self,
        *,
        service : global___ControlMessageServiceName.V = ...,
        method : global___ControlMessageServiceMethod.V = ...,
        parameters : typing.Optional[typing.Iterable[global___ControlMessageServiceParameters]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["method",b"method","parameters",b"parameters","service",b"service"]) -> None: ...
global___ControlMessage = ControlMessage
