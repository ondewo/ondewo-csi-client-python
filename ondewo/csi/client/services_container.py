from dataclasses import dataclass

from ondewo.utils.base_service_container import BaseServicesContainer

from ondewo.csi.client.services.conversations import Conversations


@dataclass
class ServicesContainer(BaseServicesContainer):
    conversations: Conversations
