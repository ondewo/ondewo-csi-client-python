# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/csi/conversation.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from ondewo.nlu import session_pb2 as ondewo_dot_nlu_dot_session__pb2
from ondewo.t2s import text_to_speech_pb2 as ondewo_dot_t2s_dot_text__to__speech__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ondewo/csi/conversation.proto',
  package='ondewo.csi',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1dondewo/csi/conversation.proto\x12\nondewo.csi\x1a\x1bgoogle/protobuf/empty.proto\x1a\x17google/rpc/status.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x18ondewo/nlu/session.proto\x1a\x1fondewo/t2s/text-to-speech.proto\"~\n\x0bS2sPipeline\x12\n\n\x02id\x18\x01 \x01(\t\x12\x17\n\x0fs2t_pipeline_id\x18\x02 \x01(\t\x12\x16\n\x0enlu_project_id\x18\x03 \x01(\t\x12\x19\n\x11nlu_language_code\x18\x04 \x01(\t\x12\x17\n\x0ft2s_pipeline_id\x18\x05 \x01(\t\"\x1b\n\rS2sPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"\x19\n\x17ListS2sPipelinesRequest\"F\n\x18ListS2sPipelinesResponse\x12*\n\tpipelines\x18\x01 \x03(\x0b\x32\x17.ondewo.csi.S2sPipeline\"\x86\x01\n\x10S2sStreamRequest\x12\x13\n\x0bpipeline_id\x18\x01 \x01(\t\x12\x12\n\nsession_id\x18\x02 \x01(\t\x12\r\n\x05\x61udio\x18\x03 \x01(\x0c\x12\x15\n\rend_of_stream\x18\x04 \x01(\x08\x12#\n\x1binitial_intent_display_name\x18\x05 \x01(\t\"\xd1\x01\n\x11S2sStreamResponse\x12\x42\n\x16\x64\x65tect_intent_response\x18\x01 \x01(\x0b\x32 .ondewo.nlu.DetectIntentResponseH\x00\x12=\n\x13synthetize_response\x18\x02 \x01(\x0b\x32\x1e.ondewo.t2s.SynthesizeResponseH\x00\x12-\n\x0bsip_trigger\x18\x03 \x01(\x0b\x32\x16.ondewo.csi.SipTriggerH\x00\x42\n\n\x08response\"\xc7\x01\n\nSipTrigger\x12\x33\n\x04type\x18\x01 \x01(\x0e\x32%.ondewo.csi.SipTrigger.SipTriggerType\x12(\n\x07\x63ontent\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\"Z\n\x0eSipTriggerType\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\n\n\x06HANGUP\x10\x01\x12\x12\n\x0eHUMAN_HANDOVER\x10\x02\x12\x0c\n\x08SEND_NOW\x10\x03\x12\t\n\x05PAUSE\x10\x04\"\x95\x01\n\x1b\x43heckUpstreamHealthResponse\x12&\n\ns2t_status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\x12&\n\nnlu_status\x18\x02 \x01(\x0b\x32\x12.google.rpc.Status\x12&\n\nt2s_status\x18\x03 \x01(\x0b\x32\x12.google.rpc.Status\"\x16\n\x14\x43ontrolStreamRequest\"\x98\x01\n\x15\x43ontrolStreamResponse\x12G\n\x0e\x63ontrol_status\x18\x01 \x01(\x0e\x32/.ondewo.csi.ControlStreamResponse.ControlStatus\"6\n\rControlStatus\x12\x11\n\rNORMAL_STREAM\x10\x00\x12\x12\n\x0e\x45MERGENCY_STOP\x10\x01\x32\x99\x05\n\rConversations\x12\x46\n\x11\x43reateS2sPipeline\x12\x17.ondewo.csi.S2sPipeline\x1a\x16.google.protobuf.Empty\"\x00\x12\x46\n\x0eGetS2sPipeline\x12\x19.ondewo.csi.S2sPipelineId\x1a\x17.ondewo.csi.S2sPipeline\"\x00\x12\x46\n\x11UpdateS2sPipeline\x12\x17.ondewo.csi.S2sPipeline\x1a\x16.google.protobuf.Empty\"\x00\x12H\n\x11\x44\x65leteS2sPipeline\x12\x19.ondewo.csi.S2sPipelineId\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x10ListS2sPipelines\x12#.ondewo.csi.ListS2sPipelinesRequest\x1a$.ondewo.csi.ListS2sPipelinesResponse\"\x00\x12N\n\tS2sStream\x12\x1c.ondewo.csi.S2sStreamRequest\x1a\x1d.ondewo.csi.S2sStreamResponse\"\x00(\x01\x30\x01\x12X\n\x13\x43heckUpstreamHealth\x12\x16.google.protobuf.Empty\x1a\'.ondewo.csi.CheckUpstreamHealthResponse\"\x00\x12[\n\x10GetControlStream\x12 .ondewo.csi.ControlStreamRequest\x1a!.ondewo.csi.ControlStreamResponse\"\x00\x30\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,google_dot_rpc_dot_status__pb2.DESCRIPTOR,google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,ondewo_dot_nlu_dot_session__pb2.DESCRIPTOR,ondewo_dot_t2s_dot_text__to__speech__pb2.DESCRIPTOR,])



_SIPTRIGGER_SIPTRIGGERTYPE = _descriptor.EnumDescriptor(
  name='SipTriggerType',
  full_name='ondewo.csi.SipTrigger.SipTriggerType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='HANGUP', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='HUMAN_HANDOVER', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SEND_NOW', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PAUSE', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=903,
  serialized_end=993,
)
_sym_db.RegisterEnumDescriptor(_SIPTRIGGER_SIPTRIGGERTYPE)

_CONTROLSTREAMRESPONSE_CONTROLSTATUS = _descriptor.EnumDescriptor(
  name='ControlStatus',
  full_name='ondewo.csi.ControlStreamResponse.ControlStatus',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NORMAL_STREAM', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='EMERGENCY_STOP', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1270,
  serialized_end=1324,
)
_sym_db.RegisterEnumDescriptor(_CONTROLSTREAMRESPONSE_CONTROLSTATUS)


_S2SPIPELINE = _descriptor.Descriptor(
  name='S2sPipeline',
  full_name='ondewo.csi.S2sPipeline',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ondewo.csi.S2sPipeline.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='s2t_pipeline_id', full_name='ondewo.csi.S2sPipeline.s2t_pipeline_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='nlu_project_id', full_name='ondewo.csi.S2sPipeline.nlu_project_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='nlu_language_code', full_name='ondewo.csi.S2sPipeline.nlu_language_code', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='t2s_pipeline_id', full_name='ondewo.csi.S2sPipeline.t2s_pipeline_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=188,
  serialized_end=314,
)


_S2SPIPELINEID = _descriptor.Descriptor(
  name='S2sPipelineId',
  full_name='ondewo.csi.S2sPipelineId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ondewo.csi.S2sPipelineId.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=316,
  serialized_end=343,
)


_LISTS2SPIPELINESREQUEST = _descriptor.Descriptor(
  name='ListS2sPipelinesRequest',
  full_name='ondewo.csi.ListS2sPipelinesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=345,
  serialized_end=370,
)


_LISTS2SPIPELINESRESPONSE = _descriptor.Descriptor(
  name='ListS2sPipelinesResponse',
  full_name='ondewo.csi.ListS2sPipelinesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='pipelines', full_name='ondewo.csi.ListS2sPipelinesResponse.pipelines', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=372,
  serialized_end=442,
)


_S2SSTREAMREQUEST = _descriptor.Descriptor(
  name='S2sStreamRequest',
  full_name='ondewo.csi.S2sStreamRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='pipeline_id', full_name='ondewo.csi.S2sStreamRequest.pipeline_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='session_id', full_name='ondewo.csi.S2sStreamRequest.session_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='audio', full_name='ondewo.csi.S2sStreamRequest.audio', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='end_of_stream', full_name='ondewo.csi.S2sStreamRequest.end_of_stream', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='initial_intent_display_name', full_name='ondewo.csi.S2sStreamRequest.initial_intent_display_name', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=445,
  serialized_end=579,
)


_S2SSTREAMRESPONSE = _descriptor.Descriptor(
  name='S2sStreamResponse',
  full_name='ondewo.csi.S2sStreamResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='detect_intent_response', full_name='ondewo.csi.S2sStreamResponse.detect_intent_response', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='synthetize_response', full_name='ondewo.csi.S2sStreamResponse.synthetize_response', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='sip_trigger', full_name='ondewo.csi.S2sStreamResponse.sip_trigger', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='response', full_name='ondewo.csi.S2sStreamResponse.response',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=582,
  serialized_end=791,
)


_SIPTRIGGER = _descriptor.Descriptor(
  name='SipTrigger',
  full_name='ondewo.csi.SipTrigger',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='ondewo.csi.SipTrigger.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='ondewo.csi.SipTrigger.content', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SIPTRIGGER_SIPTRIGGERTYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=794,
  serialized_end=993,
)


_CHECKUPSTREAMHEALTHRESPONSE = _descriptor.Descriptor(
  name='CheckUpstreamHealthResponse',
  full_name='ondewo.csi.CheckUpstreamHealthResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='s2t_status', full_name='ondewo.csi.CheckUpstreamHealthResponse.s2t_status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='nlu_status', full_name='ondewo.csi.CheckUpstreamHealthResponse.nlu_status', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='t2s_status', full_name='ondewo.csi.CheckUpstreamHealthResponse.t2s_status', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=996,
  serialized_end=1145,
)


_CONTROLSTREAMREQUEST = _descriptor.Descriptor(
  name='ControlStreamRequest',
  full_name='ondewo.csi.ControlStreamRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1147,
  serialized_end=1169,
)


_CONTROLSTREAMRESPONSE = _descriptor.Descriptor(
  name='ControlStreamResponse',
  full_name='ondewo.csi.ControlStreamResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='control_status', full_name='ondewo.csi.ControlStreamResponse.control_status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CONTROLSTREAMRESPONSE_CONTROLSTATUS,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1172,
  serialized_end=1324,
)

_LISTS2SPIPELINESRESPONSE.fields_by_name['pipelines'].message_type = _S2SPIPELINE
_S2SSTREAMRESPONSE.fields_by_name['detect_intent_response'].message_type = ondewo_dot_nlu_dot_session__pb2._DETECTINTENTRESPONSE
_S2SSTREAMRESPONSE.fields_by_name['synthetize_response'].message_type = ondewo_dot_t2s_dot_text__to__speech__pb2._SYNTHESIZERESPONSE
_S2SSTREAMRESPONSE.fields_by_name['sip_trigger'].message_type = _SIPTRIGGER
_S2SSTREAMRESPONSE.oneofs_by_name['response'].fields.append(
  _S2SSTREAMRESPONSE.fields_by_name['detect_intent_response'])
_S2SSTREAMRESPONSE.fields_by_name['detect_intent_response'].containing_oneof = _S2SSTREAMRESPONSE.oneofs_by_name['response']
_S2SSTREAMRESPONSE.oneofs_by_name['response'].fields.append(
  _S2SSTREAMRESPONSE.fields_by_name['synthetize_response'])
_S2SSTREAMRESPONSE.fields_by_name['synthetize_response'].containing_oneof = _S2SSTREAMRESPONSE.oneofs_by_name['response']
_S2SSTREAMRESPONSE.oneofs_by_name['response'].fields.append(
  _S2SSTREAMRESPONSE.fields_by_name['sip_trigger'])
_S2SSTREAMRESPONSE.fields_by_name['sip_trigger'].containing_oneof = _S2SSTREAMRESPONSE.oneofs_by_name['response']
_SIPTRIGGER.fields_by_name['type'].enum_type = _SIPTRIGGER_SIPTRIGGERTYPE
_SIPTRIGGER.fields_by_name['content'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_SIPTRIGGER_SIPTRIGGERTYPE.containing_type = _SIPTRIGGER
_CHECKUPSTREAMHEALTHRESPONSE.fields_by_name['s2t_status'].message_type = google_dot_rpc_dot_status__pb2._STATUS
_CHECKUPSTREAMHEALTHRESPONSE.fields_by_name['nlu_status'].message_type = google_dot_rpc_dot_status__pb2._STATUS
_CHECKUPSTREAMHEALTHRESPONSE.fields_by_name['t2s_status'].message_type = google_dot_rpc_dot_status__pb2._STATUS
_CONTROLSTREAMRESPONSE.fields_by_name['control_status'].enum_type = _CONTROLSTREAMRESPONSE_CONTROLSTATUS
_CONTROLSTREAMRESPONSE_CONTROLSTATUS.containing_type = _CONTROLSTREAMRESPONSE
DESCRIPTOR.message_types_by_name['S2sPipeline'] = _S2SPIPELINE
DESCRIPTOR.message_types_by_name['S2sPipelineId'] = _S2SPIPELINEID
DESCRIPTOR.message_types_by_name['ListS2sPipelinesRequest'] = _LISTS2SPIPELINESREQUEST
DESCRIPTOR.message_types_by_name['ListS2sPipelinesResponse'] = _LISTS2SPIPELINESRESPONSE
DESCRIPTOR.message_types_by_name['S2sStreamRequest'] = _S2SSTREAMREQUEST
DESCRIPTOR.message_types_by_name['S2sStreamResponse'] = _S2SSTREAMRESPONSE
DESCRIPTOR.message_types_by_name['SipTrigger'] = _SIPTRIGGER
DESCRIPTOR.message_types_by_name['CheckUpstreamHealthResponse'] = _CHECKUPSTREAMHEALTHRESPONSE
DESCRIPTOR.message_types_by_name['ControlStreamRequest'] = _CONTROLSTREAMREQUEST
DESCRIPTOR.message_types_by_name['ControlStreamResponse'] = _CONTROLSTREAMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

S2sPipeline = _reflection.GeneratedProtocolMessageType('S2sPipeline', (_message.Message,), {
  'DESCRIPTOR' : _S2SPIPELINE,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.S2sPipeline)
  })
_sym_db.RegisterMessage(S2sPipeline)

S2sPipelineId = _reflection.GeneratedProtocolMessageType('S2sPipelineId', (_message.Message,), {
  'DESCRIPTOR' : _S2SPIPELINEID,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.S2sPipelineId)
  })
_sym_db.RegisterMessage(S2sPipelineId)

ListS2sPipelinesRequest = _reflection.GeneratedProtocolMessageType('ListS2sPipelinesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2SPIPELINESREQUEST,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.ListS2sPipelinesRequest)
  })
_sym_db.RegisterMessage(ListS2sPipelinesRequest)

ListS2sPipelinesResponse = _reflection.GeneratedProtocolMessageType('ListS2sPipelinesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2SPIPELINESRESPONSE,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.ListS2sPipelinesResponse)
  })
_sym_db.RegisterMessage(ListS2sPipelinesResponse)

S2sStreamRequest = _reflection.GeneratedProtocolMessageType('S2sStreamRequest', (_message.Message,), {
  'DESCRIPTOR' : _S2SSTREAMREQUEST,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.S2sStreamRequest)
  })
_sym_db.RegisterMessage(S2sStreamRequest)

S2sStreamResponse = _reflection.GeneratedProtocolMessageType('S2sStreamResponse', (_message.Message,), {
  'DESCRIPTOR' : _S2SSTREAMRESPONSE,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.S2sStreamResponse)
  })
_sym_db.RegisterMessage(S2sStreamResponse)

SipTrigger = _reflection.GeneratedProtocolMessageType('SipTrigger', (_message.Message,), {
  'DESCRIPTOR' : _SIPTRIGGER,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.SipTrigger)
  })
_sym_db.RegisterMessage(SipTrigger)

CheckUpstreamHealthResponse = _reflection.GeneratedProtocolMessageType('CheckUpstreamHealthResponse', (_message.Message,), {
  'DESCRIPTOR' : _CHECKUPSTREAMHEALTHRESPONSE,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.CheckUpstreamHealthResponse)
  })
_sym_db.RegisterMessage(CheckUpstreamHealthResponse)

ControlStreamRequest = _reflection.GeneratedProtocolMessageType('ControlStreamRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONTROLSTREAMREQUEST,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.ControlStreamRequest)
  })
_sym_db.RegisterMessage(ControlStreamRequest)

ControlStreamResponse = _reflection.GeneratedProtocolMessageType('ControlStreamResponse', (_message.Message,), {
  'DESCRIPTOR' : _CONTROLSTREAMRESPONSE,
  '__module__' : 'ondewo.csi.conversation_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.csi.ControlStreamResponse)
  })
_sym_db.RegisterMessage(ControlStreamResponse)



_CONVERSATIONS = _descriptor.ServiceDescriptor(
  name='Conversations',
  full_name='ondewo.csi.Conversations',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1327,
  serialized_end=1992,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateS2sPipeline',
    full_name='ondewo.csi.Conversations.CreateS2sPipeline',
    index=0,
    containing_service=None,
    input_type=_S2SPIPELINE,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetS2sPipeline',
    full_name='ondewo.csi.Conversations.GetS2sPipeline',
    index=1,
    containing_service=None,
    input_type=_S2SPIPELINEID,
    output_type=_S2SPIPELINE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateS2sPipeline',
    full_name='ondewo.csi.Conversations.UpdateS2sPipeline',
    index=2,
    containing_service=None,
    input_type=_S2SPIPELINE,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteS2sPipeline',
    full_name='ondewo.csi.Conversations.DeleteS2sPipeline',
    index=3,
    containing_service=None,
    input_type=_S2SPIPELINEID,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ListS2sPipelines',
    full_name='ondewo.csi.Conversations.ListS2sPipelines',
    index=4,
    containing_service=None,
    input_type=_LISTS2SPIPELINESREQUEST,
    output_type=_LISTS2SPIPELINESRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='S2sStream',
    full_name='ondewo.csi.Conversations.S2sStream',
    index=5,
    containing_service=None,
    input_type=_S2SSTREAMREQUEST,
    output_type=_S2SSTREAMRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='CheckUpstreamHealth',
    full_name='ondewo.csi.Conversations.CheckUpstreamHealth',
    index=6,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=_CHECKUPSTREAMHEALTHRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetControlStream',
    full_name='ondewo.csi.Conversations.GetControlStream',
    index=7,
    containing_service=None,
    input_type=_CONTROLSTREAMREQUEST,
    output_type=_CONTROLSTREAMRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CONVERSATIONS)

DESCRIPTOR.services_by_name['Conversations'] = _CONVERSATIONS

# @@protoc_insertion_point(module_scope)
