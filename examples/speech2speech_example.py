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
from typing import Iterator

import pyaudio
from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
# from ondewo.nlu.client import Client
# from ondewo.nlu.client_config import ClientConfig
from ondewo.nlu.services.sessions import Sessions
from ondewo.nlu.session_pb2 import (
    QueryResult,
)

from ondewo.csi.conversation_pb2 import S2sStreamRequest
from streamer import PysoundIOStreamer


def main():
    with open('s2t.json') as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=False)
    # sessions_service: Sessions = client.services.sessions
    conversations_service: Conversations = client.services.conversations

    # Get audio stream (iterator of audio chunks)
    cai_project = "924e70ca-c786-494c-bc48-4d0999da74db"
    cai_session = "streaming-test"
    # streaming_request = PysoundIOStreamer().create_intent_request(cai_project=cai_project, cai_session=cai_session)
    streaming_request: Iterator[S2sStreamRequest] = PysoundIOStreamer().create_s2s_request()

    # get back responses
    # for response in sessions_service.streaming_detect_intent(streaming_request):
    for i, response in enumerate(conversations_service.s2s_stream(streaming_request)):
        query_result: QueryResult = response.detect_intent_response.query_result  # response.query_result
        print(f"{query_result.query_text} -> {query_result.fulfillment_messages}")
        # diagnostic_info: Dict[str, Any] = MessageToDict(query_result.diagnostic_info)

        # for message in query_result.fulfillment_messages:
        # for text in message.text.text:
        #    print(message)
        # data, rate = soundfile.read(io.BytesIO(audio_response))
        # display.Audio(data, rate=rate)


if __name__ == "__main__":
    main()
