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

from typing import Dict, Optional, List

from ondewo.nlu import context_pb2, session_pb2
from ondewo.logging.logger import logger_console

from ondewo.csi.client.client_config import ClientConfig
from ondewo.nlu.client_config import ClientConfig as NluClientConfig

from ondewo.csi.client.client import Client as CsiClient
from ondewo.nlu.client import Client as NluClient

import ondewo.nlu.agent_pb2 as agent

with open('csi.json') as fi:
    config = ClientConfig.from_json(fi.read())
with open('csi.json') as fi:
    nlu_config = NluClientConfig.from_json(fi.read())

csi_client = CsiClient(config=config)
nlu_client = NluClient(config=nlu_config)

agents = nlu_client.services.agents.list_agents(request=agent.ListAgentsRequest())

print(f"Nlu agents: {[agent.agent.parent for agent in agents.agents_with_owners]}")


def trigger_intent_csi(
    client: CsiClient,
    session_id: str,
    intent_name: str,
) -> Empty(
    """
    Trigger a specific intent in the NLU backend.

    Args:
        client: nlu client
        session_id: just the session_id
        intent_name: intent that you want to trigger

    Returns:
        Empty
    """
    request: conversation_pb2.TriggerIntentRequest = conversation_pb2.TriggerIntentRequest(
        session_id=session_id,
        text=f"Triggering Specific Intent: {intent_name}",
        context=context_pb2.Context(
                    name=f"{session_id}/contexts/exact_intent",
                    parameters=create_parameter_dict({"intent_name": intent_name}),
                    lifespan_count=1,
                    lifespan_time=10000,
                )
    )
    return client.services.conversations.trigger_intent(request)


def trigger_intent_nlu(
    client: NluClient,
    session: str,
    intent_name: str,
    language: str = "de-DE",
) -> session_pb2.DetectIntentResponse:
    """
    Trigger a specific intent in the NLU backend without intent matching.

    Args:
        client: nlu client
        session: full session to perform the trigger in ('parent/<PROJECT_ID>/agent/sessions/<SESSION_ID>')
        intent_name: intent that you want to trigger
        language: language of the project

    Returns:
        session_pb2.DetectIntentResponse
    """
    trigger_context: context_pb2.Context = context_pb2.Context(
        name=f"{session}/contexts/exact_intent",
        parameters=create_parameter_dict({"intent_name": intent_name}),
        lifespan_count=1,
        lifespan_time=10000,
    )
    request: session_pb2.DetectIntentRequest = session_pb2.DetectIntentRequest(
        session=session,
        query_input=session_pb2.QueryInput(
            text=session_pb2.TextInput(
                text=f"Triggering Specific Intent: {intent_name}",
                language_code=language
            ),
        ),
        query_params=session_pb2.QueryParameters(contexts=[trigger_context]),
    )
    return client.services.sessions.detect_intent(request)


# Maybe this should be in the client utils?
def create_parameter_dict(my_dict: Dict) -> Optional[Dict[str, context_pb2.Context.Parameter]]:
    assert isinstance(my_dict, dict) or my_dict is None, "parameter must be a dict or None"
    if my_dict is not None:
        return {
            key: context_pb2.Context.Parameter(
                display_name=key,
                value=my_dict[key]
            )
            for key in my_dict
        }
    return None


# Either:
trigger_intent_csi(csi_client, session_id, intent_name)
# Or:
trigger_intent_nlu(nlu_client, f"{project_parent}/sessions/{session_id}", intent_name, language)
