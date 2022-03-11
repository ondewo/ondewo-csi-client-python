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
import io
from typing import Any

import IPython.display as ipd
import soundfile as sf

from ondewo.t2s import text_to_speech_pb2
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.text_to_speech_pb2 import ListT2sPipelinesRequest, Text2SpeechConfig

# DESCRIPTION:
# In this example we do the following:
# 1. Create a stub which is used to connect to the server
# 2. List all avaialable pipelines and filter on english language ones
# 3. Send a synthesis request to the specified pipeline
# 4. Update the specified pipeline
# 5. Send a synthesis request to the updated pipeline
# 6. Revert the update of the specified pipeline


def synthesis_request(t2s_service: Text2Speech, **req_kwargs: Any):
    request = text_to_speech_pb2.SynthesizeRequest(**req_kwargs)
    response = t2s_service.synthesize(request=request)

    print(
        f"Length of the generated audio is {response.audio_length} sec.",
        f"Generation time is {response.generation_time} sec.",
    )

    bio = io.BytesIO(response.audio)
    audio = sf.read(bio)
    return audio


def main():
    parser = argparse.ArgumentParser(description="API example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    t2s_service: Text2Speech = client.services.text_to_speech

    # 2. List all available pipelines and filter on english language ones
    # List all t2s pipelines present on the server
    t2s_service.list_t2s_pipelines(request=ListT2sPipelinesRequest()).pipelines

    # List pipelines based on conditions
    german_pipelines = t2s_service.list_t2s_pipelines(
        request=ListT2sPipelinesRequest(languages=["de"])
    ).pipelines
    german_pipeline: Text2SpeechConfig = german_pipelines[0]

    # 3. Send a synthesis request to the specified pipeline
    # Make synthesize request to the server to get audio for given text
    audio = synthesis_request(t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])

    # Adding length scale parameter to make speech faster or slower
    audio = synthesis_request(
        t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id, length_scale=0.5
    )
    ipd.Audio(audio[0], rate=audio[1])

    # 4. Update a specified pipeline
    # Change parameter in the pipeline config. For example default length scale
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 2

    # Update pipeline
    t2s_service.update_t2s_pipeline(request=german_pipeline)

    # 5. Send a synthesis request to the updated pipeline
    # See if generated audio change according to updated config
    audio = synthesis_request(t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])

    # 6. Revert the update of the specified pipeline
    # Change parameter back to previous (length_scale = 1.0)
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 1.0
    t2s_service.update_t2s_pipeline(request=german_pipeline)


if __name__ == "__main__":
    main()
