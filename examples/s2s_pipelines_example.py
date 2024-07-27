# Copyright 2021-2024 ONDEWO GmbH
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
import json
from typing import (
    Any,
    List,
    Set,
    Tuple,
)

import grpc

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations
from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
    S2sPipeline,
    S2sPipelineId,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="S2S pipeline handling example.")
    parser.add_argument("--config", type=str, default="configs/insecure_grpc.json")
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    # https://github.com/grpc/grpc-proto/blob/master/grpc/service_config/service_config.proto
    service_config_json: str = json.dumps(
        {
            "methodConfig": [
                {
                    "name": [
                        # To apply retry to all methods, put [{}] as a value in the "name" field
                        # {}
                        # List single rpc method calls
                        {"service": "ondewo.csi.Conversations", "method": "ListS2sPipelines"},
                    ],
                    "retryPolicy": {
                        "maxAttempts": 10,
                        "initialBackoff": "1.1s",
                        "maxBackoff": "3000s",
                        "backoffMultiplier": 2,
                        "retryableStatusCodes": [
                            grpc.StatusCode.CANCELLED.name,
                            grpc.StatusCode.UNKNOWN.name,
                            grpc.StatusCode.DEADLINE_EXCEEDED.name,
                            grpc.StatusCode.NOT_FOUND.name,
                            grpc.StatusCode.RESOURCE_EXHAUSTED.name,
                            grpc.StatusCode.ABORTED.name,
                            grpc.StatusCode.INTERNAL.name,
                            grpc.StatusCode.UNAVAILABLE.name,
                            grpc.StatusCode.DATA_LOSS.name,
                        ],
                    },
                }
            ]
        }
    )

    options: Set[Tuple[str, Any]] = {
        # Define custom max message sizes: 1MB here is an arbitrary example.
        ("grpc.max_send_message_length", 1024 * 1024),
        ("grpc.max_receive_message_length", 1024 * 1024),
        # Example of setting KeepAlive options through generic channel_args
        ("grpc.keepalive_time_ms", 2 ** 31 - 1),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", False),
        ("grpc.http2.max_pings_without_data", 2),
        # Example arg requested for the feature
        ("grpc.dns_enable_srv_queries", 1),
        ("grpc.enable_retries", 1),
        ("grpc.service_config", service_config_json)
    }

    client: Client = Client(config=config, use_secure_channel=args.secure, options=options)
    conversations_service: Conversations = client.services.conversations

    # list the S2S pipelines
    list_request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    list_response: ListS2sPipelinesResponse = conversations_service.list_s2s_pipelines(list_request)
    pipelines: List[S2sPipeline] = list(list_response.pipelines)
    print(pipelines)

    # get the S2S pipeline
    print(conversations_service.get_s2s_pipeline(S2sPipelineId(id=pipelines[0].id)))

    # the code below does not work since "example_project" does not exist in the NLU server
    # # create an S2S pipeline
    # pipeline_id: str = str(uuid4())
    # pipeline: S2sPipeline = S2sPipeline(
    #     id=pipeline_id,
    #     s2t_pipeline_id="german_general",
    #     nlu_project_id="example_project",
    #     nlu_language_code="de",
    #     t2s_pipeline_id="kerstin",
    # )
    # conversations_service.create_s2s_pipeline(pipeline)
    #
    # # list S2S pipelines again
    # print(conversations_service.list_s2s_pipelines(list_request))
    #
    # # update the created S2S pipeline
    # pipeline.s2t_pipeline_id = "my_custom_german_s2t"
    # conversations_service.update_s2s_pipeline(pipeline)
    #
    # # get the u[dated S2S pipeline
    # id_request: S2sPipelineId = S2sPipelineId(id=pipeline_id)
    # print(conversations_service.get_s2s_pipeline(id_request))
    #
    # # delete the created S2S pipeline
    # print(conversations_service.delete_s2s_pipeline(id_request))
    #
    # # list S2S pipelines again
    # print(conversations_service.list_s2s_pipelines(list_request))


if __name__ == "__main__":
    main()
