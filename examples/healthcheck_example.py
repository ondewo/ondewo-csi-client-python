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

from google.protobuf.empty_pb2 import Empty

from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.client.services.conversations import Conversations


def main() -> None:
    parser = argparse.ArgumentParser(description="Healthcheck example.")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    client: Client = Client(config=config, use_secure_channel=args.secure)
    conversations_service: Conversations = client.services.conversations

    print(conversations_service.check_upstream_health(request=Empty()))


if __name__ == "__main__":
    main()
