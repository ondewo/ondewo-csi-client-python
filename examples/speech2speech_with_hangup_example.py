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
import time
import uuid
from typing import Iterator

from ondewo.logging.logger import logger_console
from ondewo.nlu.session_pb2 import QueryResult
from ondewo.sip.client.client import Client as SipClient
from ondewo.sip.client.client_config import ClientConfig as SipClientConfig
from ondewo.sip.client.services.sip import Sip
from ondewo.sip.sip_pb2 import EndCallRequest
from ondewo.t2s.text_to_speech_pb2 import SynthesizeResponse
from streamer import (
    PyAudioStreamerIn,
    PyAudioStreamerOut,
    PySoundIoStreamerIn,
    PySoundIoStreamerOut,
    StreamerInInterface,
    StreamerOutInterface,
)

from ondewo.csi.client.client import Client as CsiClient
from ondewo.csi.client.client_config import ClientConfig as CsiClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import S2sStreamRequest, SipTrigger


def main(pipeline_id: str, session_id: str, save_to_disk: bool, streamer_name: str) -> None:
    with open("csi.json") as f:
        csi_config: CsiClientConfig = CsiClientConfig.from_json(f.read())
    csi_client: CsiClient = CsiClient(config=csi_config, use_secure_channel=csi_config.grpc_cert is not None)
    conversations_service: Conversations = csi_client.services.conversations

    with open("sip.json") as f:
        sip_config: SipClientConfig = SipClientConfig.from_json(f.read())
    sip_client: SipClient = SipClient(config=sip_config, use_secure_channel=sip_config.grpc_cert is not None)
    sip_service: Sip = sip_client.services.sip

    session_id = session_id if session_id else str(uuid.uuid4())

    if "pyaudio" in streamer_name:
        # Get audio stream (iterator of audio chunks):
        streamer: StreamerInInterface = PyAudioStreamerIn()
        streaming_request: Iterator[S2sStreamRequest] = streamer.create_s2s_request(
            pipeline_id=pipeline_id,
            session_id=session_id,
            save_to_disk=save_to_disk,
        )
        player: StreamerOutInterface = PyAudioStreamerOut()

    elif "pysoundio" in streamer_name:
        # Get audio stream (iterator of audio chunks):
        streamer = PySoundIoStreamerIn()
        streaming_request = streamer.create_s2s_request(
            pipeline_id=pipeline_id, session_id=session_id, save_to_disk=save_to_disk
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
        elif response.HasField("synthetize_response"):
            t2s_response: SynthesizeResponse = response.synthetize_response
            print(f"RESPONSE \t{j}: {t2s_response.text}")
            j += 1
            streamer.mute = True  # type: ignore
            logger_console.debug("muted")
            player.play(response.synthetize_response.audio)
            # playing the audio is a bit delayed, so still wait.
            time.sleep(0.2)
            streamer.mute = False  # type: ignore
            logger_console.debug("unmuted")
        elif response.HasField("sip_trigger"):
            sip_trigger: SipTrigger = response.sip_trigger
            print(f"TRIGGER \t{j}: {sip_trigger.type}")
            j += 1
            if sip_trigger.type is SipTrigger.SipTriggerType.HANGUP:
                sip_service.end_call(EndCallRequest(hard_hangup=True))
                streamer.close()


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Streams stuff to websocket")
    parser.add_argument("--pipeline_id", default="hangup")
    parser.add_argument("--session_id", default=str(uuid.uuid4()))
    parser.add_argument("--save_to_disk", default=False)
    parser.add_argument("--streamer_name", default="pysoundio")

    args: argparse.Namespace = parser.parse_args()

    main(args.pipeline_id, args.session_id, args.save_to_disk, args.streamer_name)
