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
import wave

MONO: int = 1
RATE: int = 16000
SAMPWIDTH: int = 2


def convert_file(file):
    with open(f"audiofiles/{file}.raw", "rb") as fi:
        data = fi.read()
    with wave.open(f"audiofiles/{file}.wav", "w") as wf:
        wf.setnchannels(MONO)
        wf.setframerate(RATE)
        wf.setsampwidth(SAMPWIDTH)
        wf.writeframes(data)


convert_file("test")
