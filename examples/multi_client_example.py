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
import os
import sys
from pathlib import Path
from typing import Optional

import grpc
import ondewo.nlu.agent_pb2 as agent
import ondewo.s2t.speech_to_text_pb2 as s2t
import ondewo.t2s.text_to_speech_pb2 as t2s
from dotenv import load_dotenv
from loguru import logger as log
from ondewo.nlu.client import Client as NluClient
from ondewo.nlu.client_config import ClientConfig as NluClientConfig
from ondewo.s2t.client.client import Client as S2tClient
from ondewo.t2s.client.client import Client as T2sClient

from ondewo.csi.client.client import Client as CsiClient
from ondewo.csi.client.client_config import ClientConfig

# Load the example configuration relative to this script, so the current working
# directory does not matter.
load_dotenv(Path(__file__).with_name("environment.env"))


def main() -> None:
    """List the S2T / T2S pipelines and the NLU agents reachable at the configured host."""
    log.info("START: multi_client_example: main")
    host: str = os.getenv("ONDEWO_HOST", "localhost")
    port: str = os.getenv("ONDEWO_PORT", "50055")
    grpc_cert: Optional[str] = os.getenv("ONDEWO_GRPC_CERT") or None
    log.info(f"Connecting to ONDEWO services at {host}:{port}")

    config = ClientConfig(host=host, port=port, grpc_cert=grpc_cert)
    nlu_config = NluClientConfig(host=host, port=port, grpc_cert=grpc_cert)

    # Construct the CSI client (its RPCs are exercised in the other examples).
    CsiClient(config=config)
    s2t_client = S2tClient(config=config)
    t2s_client = T2sClient(config=config)
    nlu_client = NluClient(config=nlu_config)

    s2t_pipelines = s2t_client.services.speech_to_text.list_s2t_pipelines(request=s2t.ListS2tPipelinesRequest())
    t2s_pipelines = t2s_client.services.text_to_speech.list_t2s_pipelines(request=t2s.ListT2sPipelinesRequest())

    print(f"Speech to text pipelines: {[pipeline.id for pipeline in s2t_pipelines.pipeline_configs]}")
    print(f"Text to speech pipelines: {[pipeline.id for pipeline in t2s_pipelines.pipelines]}")

    agents = nlu_client.services.agents.list_agents(request=agent.ListAgentsRequest())

    print(f"Nlu agents: {[agent.agent.parent for agent in agents.agents_with_owners]}")
    log.info("DONE: multi_client_example: main")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as rpc_error:
        log.exception(
            f"gRPC call failed while querying ONDEWO services: code={rpc_error.code()} details={rpc_error.details()}"  # type: ignore[attr-defined]
        )
        sys.exit(1)
    except Exception:
        log.exception("multi_client_example failed.")
        sys.exit(1)
