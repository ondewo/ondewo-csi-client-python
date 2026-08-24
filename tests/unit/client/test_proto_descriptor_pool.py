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
"""Guard the layout that lets this client coexist with its sibling ONDEWO clients.

This package ships ``ondewo/csi`` **only**; the ``ondewo/nlu``, ``ondewo/s2t`` and ``ondewo/t2s``
protos it references come from the respective client wheels. Vendoring a copy of any of them here
would register a second descriptor for the same ``.proto`` file name in protobuf's default pool,
and the import that loses the race dies with ``TypeError: Couldn't build proto file into
descriptor pool: duplicate file name``.

That failure is invisible in isolation -- ``import ondewo.csi.conversation_pb2`` alone always
works -- and only appears in a process that also imports the other clients, which is precisely what
every real consumer does. It is also the failure mode a dependency bump can reintroduce, since a
new sibling wheel could start vendoring foreign protos. These tests are cheap and catch it here
rather than in a downstream service.
"""

from typing import (
    List,
    Set,
)

from google.protobuf import descriptor_pool

#: The proto packages this client consumes from sibling wheels, plus its own.
EXPECTED_PROTO_FILES: List[str] = [
    "ondewo/csi/conversation.proto",
    "ondewo/nlu/session.proto",
    "ondewo/s2t/speech-to-text.proto",
    "ondewo/t2s/text-to-speech.proto",
]


def test_csi_nlu_s2t_and_t2s_protos_share_one_descriptor_pool() -> None:
    """All four proto families import into one process without a duplicate-file collision.

    A plain import is the assertion: protobuf raises at import time when two wheels register the
    same file name, so reaching the end of this test is the guarantee.
    """
    import ondewo.csi.conversation_pb2  # noqa: F401
    import ondewo.nlu.session_pb2  # noqa: F401
    import ondewo.s2t.speech_to_text_pb2  # noqa: F401
    import ondewo.t2s.text_to_speech_pb2  # noqa: F401

    pool: descriptor_pool.DescriptorPool = descriptor_pool.Default()
    for proto_file in EXPECTED_PROTO_FILES:
        # Raises KeyError if the file never registered.
        assert pool.FindFileByName(proto_file) is not None


def test_this_distribution_ships_no_foreign_protos() -> None:
    """The installed ``ondewo`` namespace subpackages that belong to this dist are csi-only.

    The sibling ``ondewo-vtsi-client-python`` *does* vendor foreign protos and therefore has to be
    regenerated in lockstep with the service clients. This one deliberately does not, so a future
    "helpful" addition of vendored nlu protos is caught as the regression it would be.
    """
    import ondewo.csi

    csi_module_names: Set[str] = {name for name in dir(ondewo.csi) if not name.startswith("_")}

    # `ondewo.csi` must not have grown a vendored sibling package.
    assert "nlu" not in csi_module_names
    assert "s2t" not in csi_module_names
    assert "t2s" not in csi_module_names
