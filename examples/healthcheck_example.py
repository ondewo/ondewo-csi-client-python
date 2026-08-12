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

import grpc
from dotenv import load_dotenv
from google.protobuf.empty_pb2 import Empty
from loguru import logger as log

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations

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


def main() -> None:
    """Construct the client and print the upstream health-check response."""
    log.info("START: healthcheck_example: main")
    config: ClientConfig = build_config()
    use_secure_channel: bool = os.getenv("ONDEWO_USE_SECURE_CHANNEL", "false").lower() == "true"
    log.info(f"Connecting to CSI at {config.host}:{config.port} (secure={use_secure_channel})")

    client: Client = Client(config=config, use_secure_channel=use_secure_channel)
    conversations_service: Conversations = client.services.conversations

    print(conversations_service.check_upstream_health(request=Empty()))
    log.info("DONE: healthcheck_example: main")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as rpc_error:
        log.exception(
            f"gRPC health-check call failed: code={rpc_error.code()} details={rpc_error.details()}"  # type: ignore[attr-defined]
        )
        sys.exit(1)
    except Exception:
        log.exception("healthcheck_example failed.")
        sys.exit(1)
