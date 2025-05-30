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
import argparse
import time
import uuid
import wave
from typing import (
    Iterator,
    Optional,
)
from uuid import uuid4

from ondewo.nlu.session_pb2 import QueryResult
from ondewo.t2s.text_to_speech_pb2 import SynthesizeResponse

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest

AUDIO_FILE: str = "ondewo/csi/examples/audiofiles/pizza_de.wav"
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
    pipeline_id: str = "pizza",
    session_id: Optional[str] = None,
    initial_intent_display_name: Optional[str] = None,
) -> Iterator[S2sStreamRequest]:
    # create an initial request with session id specified
    yield S2sStreamRequest(
        pipeline_id=pipeline_id,
        session_id=session_id or str(uuid4()),
        initial_intent_display_name=initial_intent_display_name,  # type: ignore[arg-type]
        # In the proto its optional
    )
    for i, chunk in enumerate(audio_stream):
        yield S2sStreamRequest(audio=chunk)
        time.sleep(0.3)
    yield S2sStreamRequest(end_of_stream=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    parser.add_argument("--pipeline-id", default="pizza")
    parser.add_argument("--session-id", default=str(uuid.uuid4()))
    parser.add_argument("--intent-name")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    conversations_service: Conversations = client.services.conversations

    # Get audio stream (iterator of audio chunks)
    audio_stream: Iterator[bytes] = get_streaming_audio(AUDIO_FILE)

    # Create streaming request
    streaming_request: Iterator[S2sStreamRequest] = create_streaming_request(
        audio_stream=audio_stream,
        pipeline_id=args.pipeline_id,
        session_id=args.session_id,
        initial_intent_display_name=args.intent_name,
    )

    # get back responses
    i = 0
    j = 0
    for response in conversations_service.s2s_stream(streaming_request):
        if response.HasField("detect_intent_response"):
            query_result: QueryResult = response.detect_intent_response.query_result
            print(f"{i}: {query_result.query_text} -> {query_result.intent.display_name}")
            i += 1
            j = 0
        elif response.HasField("synthesize_response"):
            t2s_response: SynthesizeResponse = response.synthesize_response
            print(f"\t{j}: {t2s_response.text}")
            with open(f"ondewo/csi/examples/audiofiles/response_{i}-{j}.wav", "wb") as f:
                f.write(response.synthesize_response.audio)

            j += 1


if __name__ == "__main__":
    main()
