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
from typing import List
from uuid import uuid4

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
    S2sPipeline,
    S2sPipelineId,
)


def main():
    parser = argparse.ArgumentParser(description="S2S pipeline handling example.")
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    conversations_service: Conversations = client.services.conversations

    # list the S2S pipelines
    list_request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    list_response: ListS2sPipelinesResponse = conversations_service.list_s2s_pipelines(list_request)
    pipelines: List[S2sPipeline] = list(list_response.pipelines)
    print(pipelines)

    # get the S2S pipeline
    print(conversations_service.get_s2s_pipeline(S2sPipelineId(id=pipelines[0].id)))

    # create an S2S pipeline
    pipeline_id: str = str(uuid4())
    pipeline: S2sPipeline = S2sPipeline(
        id=pipeline_id,
        s2t_pipeline_id="german_general",
        nlu_project_id="example_project",
        nlu_language_code="de",
        t2s_pipeline_id="kerstin",
    )
    conversations_service.create_s2s_pipeline(pipeline)

    # list S2S pipelines again
    print(conversations_service.list_s2s_pipelines(list_request))

    # update the created S2S pipeline
    pipeline.s2t_pipeline_id = "my_custom_german_s2t"
    conversations_service.update_s2s_pipeline(pipeline)

    # get the u[dated S2S pipeline
    id_request: S2sPipelineId = S2sPipelineId(id=pipeline_id)
    print(conversations_service.get_s2s_pipeline(id_request))

    # delete the created S2S pipeline
    print(conversations_service.delete_s2s_pipeline(id_request))

    # list S2S pipelines again
    print(conversations_service.list_s2s_pipelines(list_request))

    # pipeline: S2sPipeline = S2sPipeline(
    #     id='elo_webchat',
    #     s2t_pipeline_id='german_general',
    #     nlu_project_id='7b9273eb-e0bb-4e97-8575-7b053bc80616',
    #     nlu_language_code='de',
    #     t2s_pipeline_id='kerstin',
    # )
    # conversations_service.create_s2s_pipeline(pipeline)


if __name__ == "__main__":
    main()
