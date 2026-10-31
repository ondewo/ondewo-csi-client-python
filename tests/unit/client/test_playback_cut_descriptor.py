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
"""Pin the ondewo-csi-api 5.8.0 barge-in cut contract in the generated descriptors.

ondewo-csi (the server) and its speech2speech child are built against this package. Both sides read these
fields by NUMBER on the wire, so a renumbered field or enum value would silently pair a cut with the wrong
barge-in. The numbers and types below are the frozen 5.8.0 contract; every pre-5.8.0 number must stay as it was,
which is what keeps a 5.7.0 peer wire-compatible.
"""

from typing import (
    Dict,
    Tuple,
)

import pytest
from google.protobuf.descriptor import (
    Descriptor,
    EnumDescriptor,
    FieldDescriptor,
)

from ondewo.csi import conversation_pb2

#: (field number, protobuf type) per field of PlaybackCut.
PLAYBACK_CUT_FIELDS: Dict[str, Tuple[int, int]] = {
    "playback_cut_request_id": (1, FieldDescriptor.TYPE_UINT64),
    "barge_in_epoch": (2, FieldDescriptor.TYPE_UINT64),
    "utterance_id": (3, FieldDescriptor.TYPE_STRING),
    "chunk_index": (4, FieldDescriptor.TYPE_INT32),
    "response_sequence": (5, FieldDescriptor.TYPE_UINT64),
    "written_audio_us": (6, FieldDescriptor.TYPE_INT64),
    "queued_audio_us": (7, FieldDescriptor.TYPE_INT64),
    "queued_audio_estimated": (8, FieldDescriptor.TYPE_BOOL),
    "cut_monotonic_ns": (9, FieldDescriptor.TYPE_INT64),
    "remainder_held": (10, FieldDescriptor.TYPE_BOOL),
}

#: The complete ControlStatus enum, old values included.
CONTROL_STATUS_VALUES: Dict[str, int] = {
    "OK": 0,
    "EMERGENCY_STOP": 1,
    "VAD_START_OF_SPEECH": 2,
    "BARGE_IN": 3,
    "RESUME_PLAYBACK": 4,
    "DISCARD_REMAINDER": 5,
    "PLAYBACK_RESUMED": 6,
    "PLAYBACK_DONE": 7,
    "CALL_ENDED": 8,
    "PLAYBACK_CUT": 9,
}

#: (message, field) -> (number, type) for every field 5.8.0 added to an existing message, plus the pre-existing
#: neighbours whose numbers must not move.
EXTENDED_MESSAGE_FIELDS: Dict[Tuple[str, str], Tuple[int, int]] = {
    ("ControlStreamResponse", "control_status"): (1, FieldDescriptor.TYPE_ENUM),
    ("ControlStreamResponse", "epoch"): (2, FieldDescriptor.TYPE_UINT64),
    ("ControlStreamResponse", "media_control"): (3, FieldDescriptor.TYPE_MESSAGE),
    ("ControlStreamResponse", "playback_cut_request_id"): (4, FieldDescriptor.TYPE_UINT64),
    ("SetControlStatusRequest", "control_status"): (1, FieldDescriptor.TYPE_ENUM),
    ("SetControlStatusRequest", "playback_cut"): (2, FieldDescriptor.TYPE_MESSAGE),
    ("SetControlStatusRequest", "utterance_id"): (3, FieldDescriptor.TYPE_STRING),
    ("SetControlStatusRequest", "response_sequence"): (4, FieldDescriptor.TYPE_UINT64),
    ("S2sStreamResponse", "utterance_id"): (4, FieldDescriptor.TYPE_STRING),
    ("S2sStreamResponse", "chunk_index"): (5, FieldDescriptor.TYPE_INT32),
    ("S2sStreamResponse", "last_chunk"): (6, FieldDescriptor.TYPE_BOOL),
    ("S2sStreamResponse", "turn_epoch"): (7, FieldDescriptor.TYPE_UINT64),
    ("S2sStreamResponse", "response_sequence"): (8, FieldDescriptor.TYPE_UINT64),
}


def _message(name: str) -> Descriptor:
    """
    Return the descriptor of a top-level message of ``ondewo/csi/conversation.proto``.

    Args:
        name (str):
            The message name.

    Returns:
        Descriptor:
            The message descriptor.
    """
    return conversation_pb2.DESCRIPTOR.message_types_by_name[name]


def test_playback_cut_has_exactly_the_frozen_fields() -> None:
    """PlaybackCut carries exactly the ten fields of the contract, by number and type, and nothing else."""
    descriptor: Descriptor = _message("PlaybackCut")
    actual: Dict[str, Tuple[int, int]] = {field.name: (field.number, field.type) for field in descriptor.fields}
    assert actual == PLAYBACK_CUT_FIELDS


def test_playback_cut_fields_are_plain_scalars_without_presence() -> None:
    """No PlaybackCut field is repeated, optional or in a oneof: an absent value reads as zero / empty / false."""
    descriptor: Descriptor = _message("PlaybackCut")
    assert descriptor.oneofs == []
    for field in descriptor.fields:
        assert not field.is_repeated, field.name
        assert not field.has_presence, field.name


def test_control_status_enum_appends_playback_cut_without_renumbering() -> None:
    """PLAYBACK_CUT is value 9 and every older ControlStatus value keeps its number."""
    enum: EnumDescriptor = conversation_pb2.DESCRIPTOR.enum_types_by_name["ControlStatus"]
    assert {value.name: value.number for value in enum.values} == CONTROL_STATUS_VALUES
    assert conversation_pb2.PLAYBACK_CUT == 9


@pytest.mark.parametrize(("message_and_field", "expected"), sorted(EXTENDED_MESSAGE_FIELDS.items()))
def test_extended_messages_keep_old_numbers_and_add_the_new_fields(
    message_and_field: Tuple[str, str],
    expected: Tuple[int, int],
) -> None:
    """Each new field sits at its frozen number and type, and the fields it was added next to did not move."""
    message_name, field_name = message_and_field
    field: FieldDescriptor = _message(message_name).fields_by_name[field_name]
    assert (field.number, field.type) == expected


def test_set_control_status_request_carries_a_playback_cut_message() -> None:
    """SetControlStatusRequest.playback_cut is a PlaybackCut, so a cut travels in the existing RPC."""
    field: FieldDescriptor = _message("SetControlStatusRequest").fields_by_name["playback_cut"]
    assert field.message_type is _message("PlaybackCut")


def test_playback_cut_request_id_is_a_plain_uint64_whose_zero_means_no_request() -> None:
    """A 5.7.0 server never sets field 4, which a 5.8.0 child reads as 0, i.e. no cut requested."""
    field: FieldDescriptor = _message("ControlStreamResponse").fields_by_name["playback_cut_request_id"]
    assert not field.has_presence
    assert conversation_pb2.ControlStreamResponse().playback_cut_request_id == 0


def test_a_playback_cut_report_round_trips_on_the_wire() -> None:
    """A full PLAYBACK_CUT report survives serialization with every value intact, including uint64 extremes."""
    request: conversation_pb2.SetControlStatusRequest = conversation_pb2.SetControlStatusRequest(
        control_status=conversation_pb2.PLAYBACK_CUT,
        playback_cut=conversation_pb2.PlaybackCut(
            playback_cut_request_id=2**64 - 1,
            barge_in_epoch=7,
            utterance_id="utt-1",
            chunk_index=3,
            response_sequence=42,
            written_audio_us=1_840_000,
            queued_audio_us=52_000,
            queued_audio_estimated=True,
            cut_monotonic_ns=123_456_789_012_345,
            remainder_held=True,
        ),
    )
    parsed: conversation_pb2.SetControlStatusRequest = conversation_pb2.SetControlStatusRequest.FromString(
        request.SerializeToString()
    )
    assert parsed == request
    assert parsed.HasField("playback_cut")


def test_a_5_7_0_set_control_status_request_parses_as_no_cut() -> None:
    """The bytes of a pre-5.8.0 request (field 1 only) parse with no PlaybackCut and empty PLAYBACK_DONE fields."""
    old_wire: bytes = conversation_pb2.SetControlStatusRequest(
        control_status=conversation_pb2.PLAYBACK_DONE
    ).SerializeToString()
    parsed: conversation_pb2.SetControlStatusRequest = conversation_pb2.SetControlStatusRequest.FromString(old_wire)
    assert not parsed.HasField("playback_cut")
    assert parsed.utterance_id == ""
    assert parsed.response_sequence == 0


def test_a_response_without_new_fields_serializes_to_the_same_bytes_as_before() -> None:
    """Unset new fields add no bytes, so an unchanged sender stays byte-identical on the wire."""
    response: conversation_pb2.S2sStreamResponse = conversation_pb2.S2sStreamResponse(
        utterance_id="u", chunk_index=1, last_chunk=True, turn_epoch=2
    )
    expected: bytes = b"\x22\x01u\x28\x01\x30\x01\x38\x02"
    assert response.SerializeToString() == expected
