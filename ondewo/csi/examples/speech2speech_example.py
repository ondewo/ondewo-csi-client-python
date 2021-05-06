#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2021 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from typing import Iterator, Optional
import uuid

from ondewo.nlu.session_pb2 import QueryResult
from ondewo.t2s.text_to_speech_pb2 import SynthesizeResponse

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest
from ondewo.csi.examples.streamer import (      # type: ignore
    PySoundIoStreamerIn,
    PySoundIoStreamerOut,
    PyAudioStreamerIn,
    PyAudioStreamerOut
)


def main(pipeline_id: str, session_id: str, save_to_disk: bool, streamer: str) -> None:
    session_id = session_id if session_id else str(uuid.uuid4())
    with open("csi.json") as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=True)
    conversations_service: Conversations = client.services.conversations

    if "pyaudio" in streamer:
        # Get audio stream (iterator of audio chunks):
        streaming_request: Iterator[S2sStreamRequest] = PyAudioStreamerIn().create_s2s_request(
            pipeline_id=pipeline_id,
            session_id=session_id,
            save_to_disk=save_to_disk,
        )
        player = PyAudioStreamerOut()

    if "pysoundio" in streamer:
        # Get audio stream (iterator of audio chunks):
        streaming_request: Iterator[S2sStreamRequest] = PySoundIoStreamerIn().create_s2s_request(
            pipeline_id=pipeline_id,
            session_id=session_id,
            save_to_disk=save_to_disk
        )
        player = PySoundIoStreamerOut()

    i = 0
    j = 0

    for response in conversations_service.s2s_stream(streaming_request):
        if response.HasField("detect_intent_response"):
            query_result: QueryResult = response.detect_intent_response.query_result
            print(f"INTENT {i}: {query_result.query_text} -> {query_result.intent.display_name}")
            i += 1
            j = 0
        elif response.HasField("synthetize_response"):
            t2s_response: SynthesizeResponse = response.synthetize_response
            print(f"RESPONSE \t{j}: {t2s_response.text}")
            j += 1
            player.play(response.synthetize_response.audio)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument("--pipeline_id", default="pizza")
    parser.add_argument("--session_id", default=str(uuid.uuid4()))
    parser.add_argument("--save_to_disk", default=False)
    parser.add_argument("--streamer", default="pysoundio")

    args: argparse.Namespace = parser.parse_args()

    main(args.pipeline_id, args.session_id, args.save_to_disk, args.streamer)
