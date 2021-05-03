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

from typing import Iterator

from ondewo.nlu.session_pb2 import QueryResult
from ondewo.t2s.text_to_speech_pb2 import SynthesizeResponse
from streamer import (      # type: ignore
    PyAudioStreamerIn,
    PyAudioStreamerOut,
    PysoundIOStreamerIn,
    PySoundioStreamerOut,
)

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest


def main():
    with open("csi.json") as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config)
    conversations_service: Conversations = client.services.conversations

    # # Get audio stream (iterator of audio chunks):
    # streaming_request: Iterator[S2sStreamRequest] = PyAudioStreamerIn().create_s2s_request()
    # player = PyAudioStreamerOut()

    # Get audio stream (iterator of audio chunks):
    streaming_request: Iterator[S2sStreamRequest] = PysoundIOStreamerIn().create_s2s_request()
    player = PySoundioStreamerOut()

    i = 0
    j = 0

    for response in conversations_service.s2s_stream(streaming_request):
        if response.detect_intent_response.response_id:
            query_result: QueryResult = response.detect_intent_response.query_result
            print(f"INTENT {i}: {query_result.query_text} -> {query_result.intent.display_name}")
            i += 1
            j = 0
        elif response.synthetize_response.audio:
            t2s_response: SynthesizeResponse = response.synthetize_response
            print(f"RESPONSE \t{j}: {t2s_response.text}")
            j += 1
            player.play(response.synthetize_response.audio)


if __name__ == "__main__":
    main()
