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
import os
import sys
import time
import uuid
from pathlib import Path
from typing import (
    Iterator,
    Optional,
)

import grpc
from dotenv import load_dotenv
from loguru import logger as logger_console
from ondewo.nlu.session_pb2 import QueryResult
from ondewo.t2s.text_to_speech_pb2 import SynthesizeResponse

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest
from streamer import (
    PyAudioStreamerIn,
    PyAudioStreamerOut,
    PySoundIoStreamerIn,
    PySoundIoStreamerOut,
    StreamerInInterface,
    StreamerOutInterface,
)

# Load the example configuration relative to this script, so the current working
# directory does not matter.
load_dotenv(Path(__file__).with_name("environment.env"))


def build_config() -> ClientConfig:
    """
    Build a :class:`ClientConfig` from the canonical environment variables.

    Returns:
        ClientConfig:
            A config carrying the CSI host/port and optional gRPC certificate.
    """
    return ClientConfig(
        host=os.getenv("ONDEWO_HOST", "localhost"),
        port=os.getenv("ONDEWO_PORT", "50055"),
        grpc_cert=os.getenv("ONDEWO_GRPC_CERT") or None,
    )


def main(
    pipeline_id: str,
    session_id: str,
    save_to_disk: bool,
    streamer_name: str,
    initial_intent_display_name: Optional[str] = None,
) -> None:
    """Stream microphone audio through the S2S pipeline and play back the responses."""
    logger_console.info("START: speech2speech_example: main")
    session_id = session_id if session_id else str(uuid.uuid4())
    config: ClientConfig = build_config()
    use_secure_channel: bool = os.getenv("ONDEWO_USE_SECURE_CHANNEL", "false").lower() == "true"
    logger_console.info(
        f"Connecting to CSI at {config.host}:{config.port} (secure={use_secure_channel}), "
        f"pipeline_id={pipeline_id}, session_id={session_id}, streamer={streamer_name}"
    )

    client: Client = Client(config=config, use_secure_channel=use_secure_channel)
    conversations_service: Conversations = client.services.conversations

    if "pyaudio" in streamer_name:
        # Get audio stream (iterator of audio chunks):
        streamer: StreamerInInterface = PyAudioStreamerIn()
        streaming_request: Iterator[S2sStreamRequest] = streamer.create_s2s_request(
            pipeline_id=pipeline_id,
            session_id=session_id,
            save_to_disk=save_to_disk,
            initial_intent_display_name=initial_intent_display_name,
        )
        player: StreamerOutInterface = PyAudioStreamerOut()

    elif "pysoundio" in streamer_name:
        # Get audio stream (iterator of audio chunks):
        streamer = PySoundIoStreamerIn()
        streaming_request = streamer.create_s2s_request(
            pipeline_id=pipeline_id,
            session_id=session_id,
            save_to_disk=save_to_disk,
            initial_intent_display_name=initial_intent_display_name,
        )
        player = PySoundIoStreamerOut()
    else:
        raise ValueError(f'Unknown streamer name "{streamer_name}".')

    i = 0
    j = 0

    for response in conversations_service.s2s_stream(streaming_request):
        if response.HasField("detect_intent_response"):
            query_result: QueryResult = response.detect_intent_response.query_result
            print(f"INTENT {i}: {query_result.query_text} -> {query_result.intent.display_name}")
            i += 1
            j = 0
        elif response.HasField("synthesize_response"):
            t2s_response: SynthesizeResponse = response.synthesize_response
            print(f"RESPONSE \t{j}: {t2s_response.text}")
            j += 1
            streamer.mute = True
            logger_console.debug("muted")
            player.play(response.synthesize_response.audio)
            # playing the audio is a bit delayed, so still wait.
            time.sleep(0.2)
            streamer.mute = False
            logger_console.debug("unmuted")


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument("--pipeline_id", default=os.getenv("ONDEWO_CSI_S2S_PIPELINE_ID", "pizza"))
    parser.add_argument("--session_id", default=str(uuid.uuid4()))
    parser.add_argument("--save_to_disk", default=False)
    parser.add_argument("--streamer_name", default="pysoundio")
    parser.add_argument("--intent-name")

    args: argparse.Namespace = parser.parse_args()

    try:
        main(
            pipeline_id=args.pipeline_id,
            session_id=args.session_id,
            save_to_disk=args.save_to_disk,
            streamer_name=args.streamer_name,
            initial_intent_display_name=args.intent_name,
        )
    except grpc.RpcError as rpc_error:
        logger_console.exception(
            f"gRPC streaming call failed: "
            f"code={rpc_error.code()} details={rpc_error.details()}"  # type: ignore[attr-defined]
        )
        sys.exit(1)
    except Exception:
        logger_console.exception("speech2speech_example failed.")
        sys.exit(1)
