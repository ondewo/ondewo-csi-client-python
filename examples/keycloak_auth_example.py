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
"""
Minimal example: authenticate via Keycloak (bearer) and list the S2S pipelines.

This demonstrates the *current* authentication convention of the ONDEWO CSI Python
client. The ``ClientConfig`` carries the Keycloak headless-auth fields (D18); the client
performs a one-time ROPC login with ``scope=offline_access`` against the public Keycloak
client and then attaches the auto-refreshed access token as ``Authorization: Bearer``
metadata on every RPC. The legacy ``cai-token`` / HTTP-Basic ``http_token`` and
``users.login()`` credential flows have been removed.

The Keycloak endpoint / credentials are read from environment variables so no secrets are
hard-coded; sensible non-secret defaults are provided for the non-credential fields.
"""
import os
import sys
from pathlib import Path
from typing import List

import grpc
from dotenv import load_dotenv
from loguru import logger as log

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
)

# Load the example configuration relative to this script, so the current working
# directory does not matter.
load_dotenv(Path(__file__).with_name("environment.env"))


def build_config() -> ClientConfig:
    """
    Build a :class:`ClientConfig` populated with the current Keycloak headless-auth fields.

    Values are taken from the canonical environment variables so credentials are never
    hard-coded. When all five Keycloak fields (``KEYCLOAK_URL``/``KEYCLOAK_REALM``/
    ``KEYCLOAK_CLIENT_ID``/``KEYCLOAK_USER_NAME``/``KEYCLOAK_PASSWORD``) are present the
    client sends ``Authorization: Bearer <jwt>`` on every RPC.

    Returns:
        ClientConfig:
            A config carrying host/port plus the Keycloak bearer-auth fields.
    """
    return ClientConfig(
        host=os.getenv("ONDEWO_HOST", "localhost"),
        port=os.getenv("ONDEWO_PORT", "50055"),
        grpc_cert=os.getenv("ONDEWO_GRPC_CERT") or None,
        keycloak_url=os.getenv("KEYCLOAK_URL", "https://keycloak.ondewo.com/auth"),
        realm=os.getenv("KEYCLOAK_REALM", "ondewo-ccai-platform"),
        client_id=os.getenv("KEYCLOAK_CLIENT_ID", "ondewo-nlu-cai-sdk-public"),
        username=os.getenv("KEYCLOAK_USER_NAME", "tech-user@ondewo.com"),
        password=os.getenv("KEYCLOAK_PASSWORD", ""),
        keycloak_verify_ssl=os.getenv("KEYCLOAK_VERIFY_SSL", "true").lower() == "true",
    )


def list_pipeline_ids(client: Client) -> List[str]:
    """
    Call ``ListS2sPipelines`` and return the ids of the configured pipelines.

    Args:
        client (Client):
            A constructed CSI client (its ``conversations`` service is used).

    Returns:
        List[str]:
            The id of every S2S pipeline returned by the server.
    """
    request: ListS2sPipelinesRequest = ListS2sPipelinesRequest()
    response: ListS2sPipelinesResponse = client.services.conversations.list_s2s_pipelines(request)
    return [pipeline.id for pipeline in response.pipelines]


def main() -> None:
    """Construct the client with Keycloak bearer auth and print the S2S pipeline ids."""
    log.info("START: keycloak_auth_example: main")
    config: ClientConfig = build_config()
    use_secure_channel: bool = os.getenv("ONDEWO_USE_SECURE_CHANNEL", "false").lower() == "true"
    log.info(f"Connecting to CSI at {config.host}:{config.port} (secure={use_secure_channel})")
    client: Client = Client(config=config, use_secure_channel=use_secure_channel)

    pipeline_ids: List[str] = list_pipeline_ids(client)
    log.info(f"Received {len(pipeline_ids)} S2S pipeline id(s).")
    for pipeline_id in pipeline_ids:
        print(pipeline_id)
    log.info("DONE: keycloak_auth_example: main")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as rpc_error:
        log.exception(
            f"gRPC call failed while listing S2S pipelines: "
            f"code={rpc_error.code()} details={rpc_error.details()}"  # type: ignore[attr-defined]
        )
        sys.exit(1)
    except Exception:
        log.exception("keycloak_auth_example failed.")
        sys.exit(1)
