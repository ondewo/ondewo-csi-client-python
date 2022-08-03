# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/csi/conversation.proto
"""Generated protocol buffer code."""
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from ondewo.s2t import speech_to_text_pb2 as ondewo_dot_s2t_dot_speech__to__text__pb2
from ondewo.t2s import text_to_speech_pb2 as ondewo_dot_t2s_dot_text__to__speech__pb2
from ondewo.nlu import session_pb2 as ondewo_dot_nlu_dot_session__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1dondewo/csi/conversation.proto\x12\nondewo.csi\x1a\x1bgoogle/protobuf/empty.proto\x1a\x17google/rpc/status.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x18ondewo/nlu/session.proto\x1a\x1fondewo/t2s/text-to-speech.proto\x1a\x1fondewo/s2t/speech-to-text.proto\x1a\x19google/protobuf/any.proto\"~\n\x0bS2sPipeline\x12\n\n\x02id\x18\x01 \x01(\t\x12\x17\n\x0fs2t_pipeline_id\x18\x02 \x01(\t\x12\x16\n\x0enlu_project_id\x18\x03 \x01(\t\x12\x19\n\x11nlu_language_code\x18\x04 \x01(\t\x12\x17\n\x0ft2s_pipeline_id\x18\x05 \x01(\t\"\x1b\n\rS2sPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"\x19\n\x17ListS2sPipelinesRequest\"F\n\x18ListS2sPipelinesResponse\x12*\n\tpipelines\x18\x01 \x03(\x0b\x32\x17.ondewo.csi.S2sPipeline\"\x86\x01\n\x10S2sStreamRequest\x12\x13\n\x0bpipeline_id\x18\x01 \x01(\t\x12\x12\n\nsession_id\x18\x02 \x01(\t\x12\r\n\x05\x61udio\x18\x03 \x01(\x0c\x12\x15\n\rend_of_stream\x18\x04 \x01(\x08\x12#\n\x1binitial_intent_display_name\x18\x05 \x01(\t\"\xd1\x01\n\x11S2sStreamResponse\x12\x42\n\x16\x64\x65tect_intent_response\x18\x01 \x01(\x0b\x32 .ondewo.nlu.DetectIntentResponseH\x00\x12=\n\x13synthetize_response\x18\x02 \x01(\x0b\x32\x1e.ondewo.t2s.SynthesizeResponseH\x00\x12-\n\x0bsip_trigger\x18\x03 \x01(\x0b\x32\x16.ondewo.csi.SipTriggerH\x00\x42\n\n\x08response\"\xc7\x01\n\nSipTrigger\x12\x33\n\x04type\x18\x01 \x01(\x0e\x32%.ondewo.csi.SipTrigger.SipTriggerType\x12(\n\x07\x63ontent\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\"Z\n\x0eSipTriggerType\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\n\n\x06HANGUP\x10\x01\x12\x12\n\x0eHUMAN_HANDOVER\x10\x02\x12\x0c\n\x08SEND_NOW\x10\x03\x12\t\n\x05PAUSE\x10\x04\"\x95\x01\n\x1b\x43heckUpstreamHealthResponse\x12&\n\ns2t_status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\x12&\n\nnlu_status\x18\x02 \x01(\x0b\x32\x12.google.rpc.Status\x12&\n\nt2s_status\x18\x03 \x01(\x0b\x32\x12.google.rpc.Status\"\x16\n\x14\x43ontrolStreamRequest\"J\n\x15\x43ontrolStreamResponse\x12\x31\n\x0e\x63ontrol_status\x18\x01 \x01(\x0e\x32\x19.ondewo.csi.ControlStatus\"L\n\x17SetControlStatusRequest\x12\x31\n\x0e\x63ontrol_status\x18\x01 \x01(\x0e\x32\x19.ondewo.csi.ControlStatus\"\x88\x01\n\x18SetControlStatusResponse\x12\x35\n\x12old_control_status\x18\x01 \x01(\x0e\x32\x19.ondewo.csi.ControlStatus\x12\x35\n\x12new_control_status\x18\x02 \x01(\x0e\x32\x19.ondewo.csi.ControlStatus\"\x84\x01\n\x12\x43ondtionValueUnion\x12\x13\n\tint_value\x18\x01 \x01(\x03H\x00\x12\x15\n\x0b\x66loat_value\x18\x02 \x01(\x02H\x00\x12\x34\n\x0e\x64\x61tetime_value\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x00\x42\x0c\n\nUnionOneof\"C\n\tCondition\x12\'\n\x04type\x18\x01 \x01(\x0e\x32\x19.ondewo.csi.ConditionType\x12\r\n\x05value\x18\x02 \x01(\t\"\xab\x02\n\x1f\x43ontrolMessageServiceParameters\x12/\n\nt2s_config\x18\x01 \x01(\x0b\x32\x19.ondewo.t2s.RequestConfigH\x00\x12\x39\n\ns2t_config\x18\x02 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfigH\x00\x12\x13\n\x0btransfer_id\x18\x03 \x01(\t\x12\x0c\n\x04text\x18\x04 \x01(\t\x12\x11\n\twav_files\x18\x05 \x03(\x0c\x12.\n\x0f\x63ondition_start\x18\x06 \x01(\x0b\x32\x15.ondewo.csi.Condition\x12,\n\rcondition_end\x18\x07 \x01(\x0b\x32\x15.ondewo.csi.ConditionB\x08\n\x06\x63onfig\"\xc2\x01\n\x0e\x43ontrolMessage\x12\x36\n\x07service\x18\x01 \x01(\x0e\x32%.ondewo.csi.ControlMessageServiceName\x12\x37\n\x06method\x18\x02 \x01(\x0e\x32\'.ondewo.csi.ControlMessageServiceMethod\x12?\n\nparameters\x18\x03 \x01(\x0b\x32+.ondewo.csi.ControlMessageServiceParameters*+\n\rControlStatus\x12\x06\n\x02OK\x10\x00\x12\x12\n\x0e\x45MERGENCY_STOP\x10\x01*l\n\x19\x43ontrolMessageServiceName\x12\x0f\n\x0bUNKNOWNNAME\x10\x00\x12\x0e\n\nondewo_s2t\x10\x01\x12\x0e\n\nondewo_t2s\x10\x02\x12\x0e\n\nondewo_nlu\x10\x03\x12\x0e\n\nondewo_sip\x10\x04*\xe0\x01\n\x1b\x43ontrolMessageServiceMethod\x12\x11\n\rUNKNOWNMETHOD\x10\x00\x12\x11\n\rupdate_config\x10\x01\x12\x0f\n\x0bundo_config\x10\x02\x12\x10\n\x0creset_config\x10\x03\x12\x0c\n\x08\x65nd_call\x10\x04\x12\x11\n\rtransfer_call\x10\x05\x12\x12\n\x0eplay_wav_files\x10\x06\x12\r\n\tplay_text\x10\x07\x12\x08\n\x04mute\x10\x08\x12\x0b\n\x07un_mute\x10\t\x12\x1d\n\x19stop_all_control_messages\x10\n*\\\n\rConditionType\x12\x0e\n\nUNKNOWTYPE\x10\x00\x12\r\n\timmediate\x10\x01\x12\x0c\n\x08\x64uration\x10\x02\x12\x0c\n\x08\x64\x61tetime\x10\x03\x12\x10\n\x0cinteractions\x10\x04\x32\xfa\x05\n\rConversations\x12\x46\n\x11\x43reateS2sPipeline\x12\x17.ondewo.csi.S2sPipeline\x1a\x16.google.protobuf.Empty\"\x00\x12\x46\n\x0eGetS2sPipeline\x12\x19.ondewo.csi.S2sPipelineId\x1a\x17.ondewo.csi.S2sPipeline\"\x00\x12\x46\n\x11UpdateS2sPipeline\x12\x17.ondewo.csi.S2sPipeline\x1a\x16.google.protobuf.Empty\"\x00\x12H\n\x11\x44\x65leteS2sPipeline\x12\x19.ondewo.csi.S2sPipelineId\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x10ListS2sPipelines\x12#.ondewo.csi.ListS2sPipelinesRequest\x1a$.ondewo.csi.ListS2sPipelinesResponse\"\x00\x12N\n\tS2sStream\x12\x1c.ondewo.csi.S2sStreamRequest\x1a\x1d.ondewo.csi.S2sStreamResponse\"\x00(\x01\x30\x01\x12X\n\x13\x43heckUpstreamHealth\x12\x16.google.protobuf.Empty\x1a\'.ondewo.csi.CheckUpstreamHealthResponse\"\x00\x12[\n\x10GetControlStream\x12 .ondewo.csi.ControlStreamRequest\x1a!.ondewo.csi.ControlStreamResponse\"\x00\x30\x01\x12_\n\x10SetControlStatus\x12#.ondewo.csi.SetControlStatusRequest\x1a$.ondewo.csi.SetControlStatusResponse\"\x00\x62\x06proto3')

_CONTROLSTATUS = DESCRIPTOR.enum_types_by_name['ControlStatus']
ControlStatus = enum_type_wrapper.EnumTypeWrapper(_CONTROLSTATUS)
_CONTROLMESSAGESERVICENAME = DESCRIPTOR.enum_types_by_name['ControlMessageServiceName']
ControlMessageServiceName = enum_type_wrapper.EnumTypeWrapper(_CONTROLMESSAGESERVICENAME)
_CONTROLMESSAGESERVICEMETHOD = DESCRIPTOR.enum_types_by_name['ControlMessageServiceMethod']
ControlMessageServiceMethod = enum_type_wrapper.EnumTypeWrapper(_CONTROLMESSAGESERVICEMETHOD)
_CONDITIONTYPE = DESCRIPTOR.enum_types_by_name['ConditionType']
ConditionType = enum_type_wrapper.EnumTypeWrapper(_CONDITIONTYPE)
OK = 0
EMERGENCY_STOP = 1
UNKNOWNNAME = 0
ondewo_s2t = 1
ondewo_t2s = 2
ondewo_nlu = 3
ondewo_sip = 4
UNKNOWNMETHOD = 0
update_config = 1
undo_config = 2
reset_config = 3
end_call = 4
transfer_call = 5
play_wav_files = 6
play_text = 7
mute = 8
un_mute = 9
stop_all_control_messages = 10
UNKNOWTYPE = 0
immediate = 1
duration = 2
datetime = 3
interactions = 4


_S2SPIPELINE = DESCRIPTOR.message_types_by_name['S2sPipeline']
_S2SPIPELINEID = DESCRIPTOR.message_types_by_name['S2sPipelineId']
_LISTS2SPIPELINESREQUEST = DESCRIPTOR.message_types_by_name['ListS2sPipelinesRequest']
_LISTS2SPIPELINESRESPONSE = DESCRIPTOR.message_types_by_name['ListS2sPipelinesResponse']
_S2SSTREAMREQUEST = DESCRIPTOR.message_types_by_name['S2sStreamRequest']
_S2SSTREAMRESPONSE = DESCRIPTOR.message_types_by_name['S2sStreamResponse']
_SIPTRIGGER = DESCRIPTOR.message_types_by_name['SipTrigger']
_CHECKUPSTREAMHEALTHRESPONSE = DESCRIPTOR.message_types_by_name['CheckUpstreamHealthResponse']
_CONTROLSTREAMREQUEST = DESCRIPTOR.message_types_by_name['ControlStreamRequest']
_CONTROLSTREAMRESPONSE = DESCRIPTOR.message_types_by_name['ControlStreamResponse']
_SETCONTROLSTATUSREQUEST = DESCRIPTOR.message_types_by_name['SetControlStatusRequest']
_SETCONTROLSTATUSRESPONSE = DESCRIPTOR.message_types_by_name['SetControlStatusResponse']
_CONDTIONVALUEUNION = DESCRIPTOR.message_types_by_name['CondtionValueUnion']
_CONDITION = DESCRIPTOR.message_types_by_name['Condition']
_CONTROLMESSAGESERVICEPARAMETERS = DESCRIPTOR.message_types_by_name['ControlMessageServiceParameters']
_CONTROLMESSAGE = DESCRIPTOR.message_types_by_name['ControlMessage']
_SIPTRIGGER_SIPTRIGGERTYPE = _SIPTRIGGER.enum_types_by_name['SipTriggerType']
S2sPipeline = _reflection.GeneratedProtocolMessageType('S2sPipeline', (_message.Message,), {
    'DESCRIPTOR': _S2SPIPELINE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.S2sPipeline)
})
_sym_db.RegisterMessage(S2sPipeline)

S2sPipelineId = _reflection.GeneratedProtocolMessageType('S2sPipelineId', (_message.Message,), {
    'DESCRIPTOR': _S2SPIPELINEID,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.S2sPipelineId)
})
_sym_db.RegisterMessage(S2sPipelineId)

ListS2sPipelinesRequest = _reflection.GeneratedProtocolMessageType('ListS2sPipelinesRequest', (_message.Message,), {
    'DESCRIPTOR': _LISTS2SPIPELINESREQUEST,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ListS2sPipelinesRequest)
})
_sym_db.RegisterMessage(ListS2sPipelinesRequest)

ListS2sPipelinesResponse = _reflection.GeneratedProtocolMessageType('ListS2sPipelinesResponse', (_message.Message,), {
    'DESCRIPTOR': _LISTS2SPIPELINESRESPONSE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ListS2sPipelinesResponse)
})
_sym_db.RegisterMessage(ListS2sPipelinesResponse)

S2sStreamRequest = _reflection.GeneratedProtocolMessageType('S2sStreamRequest', (_message.Message,), {
    'DESCRIPTOR': _S2SSTREAMREQUEST,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.S2sStreamRequest)
})
_sym_db.RegisterMessage(S2sStreamRequest)

S2sStreamResponse = _reflection.GeneratedProtocolMessageType('S2sStreamResponse', (_message.Message,), {
    'DESCRIPTOR': _S2SSTREAMRESPONSE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.S2sStreamResponse)
})
_sym_db.RegisterMessage(S2sStreamResponse)

SipTrigger = _reflection.GeneratedProtocolMessageType('SipTrigger', (_message.Message,), {
    'DESCRIPTOR': _SIPTRIGGER,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.SipTrigger)
})
_sym_db.RegisterMessage(SipTrigger)

CheckUpstreamHealthResponse = _reflection.GeneratedProtocolMessageType('CheckUpstreamHealthResponse', (_message.Message,), {
    'DESCRIPTOR': _CHECKUPSTREAMHEALTHRESPONSE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.CheckUpstreamHealthResponse)
})
_sym_db.RegisterMessage(CheckUpstreamHealthResponse)

ControlStreamRequest = _reflection.GeneratedProtocolMessageType('ControlStreamRequest', (_message.Message,), {
    'DESCRIPTOR': _CONTROLSTREAMREQUEST,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ControlStreamRequest)
})
_sym_db.RegisterMessage(ControlStreamRequest)

ControlStreamResponse = _reflection.GeneratedProtocolMessageType('ControlStreamResponse', (_message.Message,), {
    'DESCRIPTOR': _CONTROLSTREAMRESPONSE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ControlStreamResponse)
})
_sym_db.RegisterMessage(ControlStreamResponse)

SetControlStatusRequest = _reflection.GeneratedProtocolMessageType('SetControlStatusRequest', (_message.Message,), {
    'DESCRIPTOR': _SETCONTROLSTATUSREQUEST,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.SetControlStatusRequest)
})
_sym_db.RegisterMessage(SetControlStatusRequest)

SetControlStatusResponse = _reflection.GeneratedProtocolMessageType('SetControlStatusResponse', (_message.Message,), {
    'DESCRIPTOR': _SETCONTROLSTATUSRESPONSE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.SetControlStatusResponse)
})
_sym_db.RegisterMessage(SetControlStatusResponse)

CondtionValueUnion = _reflection.GeneratedProtocolMessageType('CondtionValueUnion', (_message.Message,), {
    'DESCRIPTOR': _CONDTIONVALUEUNION,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.CondtionValueUnion)
})
_sym_db.RegisterMessage(CondtionValueUnion)

Condition = _reflection.GeneratedProtocolMessageType('Condition', (_message.Message,), {
    'DESCRIPTOR': _CONDITION,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.Condition)
})
_sym_db.RegisterMessage(Condition)

ControlMessageServiceParameters = _reflection.GeneratedProtocolMessageType('ControlMessageServiceParameters', (_message.Message,), {
    'DESCRIPTOR': _CONTROLMESSAGESERVICEPARAMETERS,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ControlMessageServiceParameters)
})
_sym_db.RegisterMessage(ControlMessageServiceParameters)

ControlMessage = _reflection.GeneratedProtocolMessageType('ControlMessage', (_message.Message,), {
    'DESCRIPTOR': _CONTROLMESSAGE,
    '__module__': 'ondewo.csi.conversation_pb2'
    # @@protoc_insertion_point(class_scope:ondewo.csi.ControlMessage)
})
_sym_db.RegisterMessage(ControlMessage)

_CONVERSATIONS = DESCRIPTOR.services_by_name['Conversations']
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _CONTROLSTATUS._serialized_start = 2260
    _CONTROLSTATUS._serialized_end = 2303
    _CONTROLMESSAGESERVICENAME._serialized_start = 2305
    _CONTROLMESSAGESERVICENAME._serialized_end = 2413
    _CONTROLMESSAGESERVICEMETHOD._serialized_start = 2416
    _CONTROLMESSAGESERVICEMETHOD._serialized_end = 2640
    _CONDITIONTYPE._serialized_start = 2642
    _CONDITIONTYPE._serialized_end = 2734
    _S2SPIPELINE._serialized_start = 281
    _S2SPIPELINE._serialized_end = 407
    _S2SPIPELINEID._serialized_start = 409
    _S2SPIPELINEID._serialized_end = 436
    _LISTS2SPIPELINESREQUEST._serialized_start = 438
    _LISTS2SPIPELINESREQUEST._serialized_end = 463
    _LISTS2SPIPELINESRESPONSE._serialized_start = 465
    _LISTS2SPIPELINESRESPONSE._serialized_end = 535
    _S2SSTREAMREQUEST._serialized_start = 538
    _S2SSTREAMREQUEST._serialized_end = 672
    _S2SSTREAMRESPONSE._serialized_start = 675
    _S2SSTREAMRESPONSE._serialized_end = 884
    _SIPTRIGGER._serialized_start = 887
    _SIPTRIGGER._serialized_end = 1086
    _SIPTRIGGER_SIPTRIGGERTYPE._serialized_start = 996
    _SIPTRIGGER_SIPTRIGGERTYPE._serialized_end = 1086
    _CHECKUPSTREAMHEALTHRESPONSE._serialized_start = 1089
    _CHECKUPSTREAMHEALTHRESPONSE._serialized_end = 1238
    _CONTROLSTREAMREQUEST._serialized_start = 1240
    _CONTROLSTREAMREQUEST._serialized_end = 1262
    _CONTROLSTREAMRESPONSE._serialized_start = 1264
    _CONTROLSTREAMRESPONSE._serialized_end = 1338
    _SETCONTROLSTATUSREQUEST._serialized_start = 1340
    _SETCONTROLSTATUSREQUEST._serialized_end = 1416
    _SETCONTROLSTATUSRESPONSE._serialized_start = 1419
    _SETCONTROLSTATUSRESPONSE._serialized_end = 1555
    _CONDTIONVALUEUNION._serialized_start = 1558
    _CONDTIONVALUEUNION._serialized_end = 1690
    _CONDITION._serialized_start = 1692
    _CONDITION._serialized_end = 1759
    _CONTROLMESSAGESERVICEPARAMETERS._serialized_start = 1762
    _CONTROLMESSAGESERVICEPARAMETERS._serialized_end = 2061
    _CONTROLMESSAGE._serialized_start = 2064
    _CONTROLMESSAGE._serialized_end = 2258
    _CONVERSATIONS._serialized_start = 2737
    _CONVERSATIONS._serialized_end = 3499
# @@protoc_insertion_point(module_scope)
