#!/usr/bin/env python
# coding: utf-8
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
import wave
from typing import Iterator

from ondewo.nlu.session_pb2 import QueryResult

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest

AUDIO_FILE: str = "examples/audiofiles/pizza_de.wav"
CHUNK_SIZE: int = 8000


# We are going to make to send the file chunk-by-chunk to simulate a stream
def get_streaming_audio(audio_path: str) -> Iterator[bytes]:
    with wave.open(audio_path) as w:
        chunk: bytes = w.readframes(CHUNK_SIZE)
        while chunk != b"":
            yield chunk
            chunk = w.readframes(CHUNK_SIZE)


def create_streaming_request(
    audio_stream: Iterator[bytes],
) -> Iterator[S2sStreamRequest]:
    for i, chunk in enumerate(audio_stream):
        yield S2sStreamRequest(audio=chunk)
    yield S2sStreamRequest(end_of_stream=True)


def main():
    parser = argparse.ArgumentParser(description="Streaming example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    conversations_service: Conversations = client.services.conversations

    # Get audio stream (iterator of audio chunks)
    audio_stream: Iterator[bytes] = get_streaming_audio(AUDIO_FILE)

    # Create streaming request
    streaming_request: Iterator[S2sStreamRequest] = create_streaming_request(audio_stream)

    # get back responses
    for i, response in enumerate(conversations_service.s2s_stream(streaming_request)):
        query_result: QueryResult = response.detect_intent_response.query_result
        print(f"{query_result.query_text} -> {query_result.fulfillment_messages}")
        with open(f"examples/audiofiles/response_{i + 1}.wav", "wb") as f:
            f.write(response.synthetize_response.audio)
        # data, rate = soundfile.read(io.BytesIO(response.synthetize_response.audio))
        # display.Audio(data, rate=rate)


if __name__ == "__main__":
    main()
