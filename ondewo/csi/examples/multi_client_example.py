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

import ondewo.s2t.speech_to_text_pb2 as s2t
import ondewo.t2s.text_to_speech_pb2 as t2s
from ondewo.s2t.client.client import Client as S2tClient
from ondewo.t2s.client.client import Client as T2sClient

from ondewo.csi.client.client import Client as CsiClient
from ondewo.csi.client.client_config import ClientConfig

with open("examples/configs/csi.json") as fi:
    config = ClientConfig.from_json(fi.read())

csi_client = CsiClient(config=config)
s2t_client = S2tClient(config=config)
t2s_client = T2sClient(config=config)

s2t_pipelines = s2t_client.services.speech_to_text.list_s2t_pipelines(request=s2t.ListS2tPipelinesRequest())
t2s_pipelines = t2s_client.services.text_to_speech.list_t2s_pipelines(request=t2s.ListT2sPipelinesRequest())

print([pipeline.id for pipeline in s2t_pipelines.pipeline_configs])
print([pipeline.id for pipeline in t2s_pipelines.pipelines])
