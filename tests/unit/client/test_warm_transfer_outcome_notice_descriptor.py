# Copyright 2021-2026 ONDEWO GmbH
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
"""Pin the ondewo-csi-api 5.9.0 warm-transfer outcome notice contract in the generated code.

ondewo-sip hands the bot a warm-transfer outcome through ``Conversations.DeliverWarmTransferOutcomeNotice``, and
ondewo-csi serves it. Both sides read the fields and enum values by NUMBER on the wire, so the numbers below are the
frozen 5.9.0 contract. The media-control messages the notice was deliberately kept OUT of must stay byte-unchanged.
"""

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import pytest
from google.protobuf.descriptor import (
    Descriptor,
    EnumDescriptor,
    FieldDescriptor,
    MethodDescriptor,
)

from ondewo.csi import (
    conversation_pb2,
    conversation_pb2_grpc,
)

#: (field number, protobuf type) per field of WarmTransferOutcomeNotice.
NOTICE_FIELDS: Dict[str, Tuple[int, int]] = {
    "request_id": (1, FieldDescriptor.TYPE_STRING),
    "outcome": (2, FieldDescriptor.TYPE_ENUM),
    "intro_session": (3, FieldDescriptor.TYPE_STRING),
    "callee_display_name": (4, FieldDescriptor.TYPE_STRING),
    "cause": (5, FieldDescriptor.TYPE_STRING),
    "fallback_text": (6, FieldDescriptor.TYPE_STRING),
}

#: The complete enums 5.9.0 added.
ENUMS: Dict[str, Dict[str, int]] = {
    "WarmTransferOutcome": {
        "WARM_TRANSFER_OUTCOME_UNSPECIFIED": 0,
        "WARM_TRANSFER_OUTCOME_DECLINED": 1,
        "WARM_TRANSFER_OUTCOME_UNREACHABLE": 2,
        "WARM_TRANSFER_OUTCOME_DELEGATION_EXPIRED": 3,
    },
    "WarmTransferOutcomeNoticeStatus": {
        "WARM_TRANSFER_OUTCOME_NOTICE_STATUS_UNSPECIFIED": 0,
        "WARM_TRANSFER_OUTCOME_NOTICE_STATUS_QUEUED": 1,
        "WARM_TRANSFER_OUTCOME_NOTICE_STATUS_DUPLICATE": 2,
        "WARM_TRANSFER_OUTCOME_NOTICE_STATUS_DISABLED": 3,
        "WARM_TRANSFER_OUTCOME_NOTICE_STATUS_INVALID": 4,
    },
}

#: The field names, in number order, of the two media-control messages the notice must NOT have joined.
UNCHANGED_MESSAGES: Dict[str, List[str]] = {
    "CallMediaControlLevel": ["bot_muted", "listening_paused", "generation", "reason"],
    "SetCallMediaControlResponse": ["applied", "changed", "stale", "bot_playback_in_flight", "refusal_reason"],
}


def test_the_service_carries_the_unary_notice_rpc() -> None:
    """``DeliverWarmTransferOutcomeNotice`` is a unary RPC from the notice to its response."""
    method: MethodDescriptor = conversation_pb2.DESCRIPTOR.services_by_name["Conversations"].methods_by_name[
        "DeliverWarmTransferOutcomeNotice"
    ]
    assert method.input_type.full_name == "ondewo.csi.WarmTransferOutcomeNotice"
    assert method.output_type.full_name == "ondewo.csi.WarmTransferOutcomeNoticeResponse"
    assert not method.client_streaming
    assert not method.server_streaming


def test_the_generated_grpc_module_exposes_the_notice_rpc() -> None:
    """The stub, the servicer base and the experimental API in ``conversation_pb2_grpc`` all carry the RPC."""
    assert hasattr(conversation_pb2_grpc.ConversationsServicer, "DeliverWarmTransferOutcomeNotice")
    assert hasattr(conversation_pb2_grpc.Conversations, "DeliverWarmTransferOutcomeNotice")
    assert "DeliverWarmTransferOutcomeNotice" in conversation_pb2_grpc.ConversationsStub.__init__.__code__.co_names


@pytest.mark.parametrize("field_name", sorted(NOTICE_FIELDS))
def test_every_notice_field_has_its_frozen_number_and_type(field_name: str) -> None:
    """Every ``WarmTransferOutcomeNotice`` field keeps its 5.9.0 number and type."""
    message: Descriptor = conversation_pb2.DESCRIPTOR.message_types_by_name["WarmTransferOutcomeNotice"]
    field: FieldDescriptor = message.fields_by_name[field_name]
    assert (field.number, field.type) == NOTICE_FIELDS[field_name]


def test_the_notice_has_no_field_beyond_the_contract() -> None:
    """A field the contract does not name would be read by nobody on the other side."""
    message: Descriptor = conversation_pb2.DESCRIPTOR.message_types_by_name["WarmTransferOutcomeNotice"]
    assert set(message.fields_by_name) == set(NOTICE_FIELDS)
    outcome_enum: Optional[EnumDescriptor] = message.fields_by_name["outcome"].enum_type
    assert outcome_enum is not None
    assert outcome_enum.full_name == "ondewo.csi.WarmTransferOutcome"


def test_the_response_carries_only_its_status() -> None:
    """``WarmTransferOutcomeNoticeResponse.status`` is field 1 of the status enum, and the only field."""
    message: Descriptor = conversation_pb2.DESCRIPTOR.message_types_by_name["WarmTransferOutcomeNoticeResponse"]
    assert list(message.fields_by_name) == ["status"]
    status: FieldDescriptor = message.fields_by_name["status"]
    assert status.number == 1
    status_enum: Optional[EnumDescriptor] = status.enum_type
    assert status_enum is not None
    assert status_enum.full_name == "ondewo.csi.WarmTransferOutcomeNoticeStatus"


@pytest.mark.parametrize("enum_name", sorted(ENUMS))
def test_every_enum_has_exactly_its_frozen_values(enum_name: str) -> None:
    """Both new enums are top-level and carry exactly their 5.9.0 values."""
    enum: EnumDescriptor = conversation_pb2.DESCRIPTOR.enum_types_by_name[enum_name]
    assert {value.name: value.number for value in enum.values} == ENUMS[enum_name]


@pytest.mark.parametrize("message_name", sorted(UNCHANGED_MESSAGES))
def test_the_media_control_messages_are_unchanged(message_name: str) -> None:
    """The notice is its own RPC, not a field of the media-control level or its response."""
    message: Descriptor = conversation_pb2.DESCRIPTOR.message_types_by_name[message_name]
    names: List[str] = [field.name for field in sorted(message.fields, key=lambda field: field.number)]
    assert names == UNCHANGED_MESSAGES[message_name]
    assert [field.number for field in sorted(message.fields, key=lambda field: field.number)] == list(
        range(1, len(names) + 1)
    )
