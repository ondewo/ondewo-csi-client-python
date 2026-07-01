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
from typing import List

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
)


def build_config() -> ClientConfig:
    """
    Build a :class:`ClientConfig` populated with the current Keycloak headless-auth fields.

    Values are taken from environment variables so credentials are never hard-coded. When
    all five Keycloak fields (``keycloak_url``/``realm``/``client_id``/username/password)
    are present the client sends ``Authorization: Bearer <jwt>`` on every RPC.

    Returns:
        ClientConfig:
            A config carrying host/port plus the Keycloak bearer-auth fields.
    """
    return ClientConfig(
        host=os.getenv("ONDEWO_CSI_HOST", "localhost"),
        port=os.getenv("ONDEWO_CSI_PORT", "50055"),
        keycloak_url=os.getenv("ONDEWO_KEYCLOAK_URL", "https://keycloak.ondewo.com/auth"),
        realm=os.getenv("ONDEWO_KEYCLOAK_REALM", "ondewo-ccai-platform"),
        client_id=os.getenv("ONDEWO_KEYCLOAK_CLIENT_ID", "ondewo-nlu-cai-sdk-public"),
        username=os.getenv("ONDEWO_KEYCLOAK_USERNAME", "tech-user@ondewo.com"),
        password=os.getenv("ONDEWO_KEYCLOAK_PASSWORD", ""),
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
    config: ClientConfig = build_config()
    client: Client = Client(config=config, use_secure_channel=config.grpc_cert is not None)

    for pipeline_id in list_pipeline_ids(client):
        print(pipeline_id)


if __name__ == "__main__":
    main()
