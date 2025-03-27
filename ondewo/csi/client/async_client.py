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
from typing import (
    Any,
    Optional,
    Set,
    Tuple,
)

from ondewo.utils.async_base_client import AsyncBaseClient

from ondewo.csi.client.async_services_container import AsyncServicesContainer
from ondewo.csi.client.client_config import BaseClientConfig
from ondewo.csi.client.services.async_conversations import Conversations


class AsyncClient(AsyncBaseClient):
    """
    The core asynchronous Python client for interacting with ONDEWO s2t services.
    """

    def _initialize_services(
        self,
        config: BaseClientConfig,
        use_secure_channel: bool,
        options: Optional[Set[Tuple[str, Any]]] = None,
    ) -> None:
        """
        Initialize the asynchronous service clients, login with the current config,
        and set up the services in self.services.

        Args:
            config (ClientConfig): Configuration for the client.
            use_secure_channel (bool): Whether to use a secure gRPC channel.
            options (Optional[Set[Tuple[str, Any]]]): Additional options for the gRPC channel.
        """
        self.services: AsyncServicesContainer = AsyncServicesContainer(
            conversations=Conversations(config=config, use_secure_channel=use_secure_channel, options=options),
        )
