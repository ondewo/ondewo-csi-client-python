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
import wave
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger as log

# Load the example configuration relative to this script, so the current working
# directory does not matter.
load_dotenv(Path(__file__).with_name("environment.env"))

MONO: int = 1
RATE: int = 16000
SAMPWIDTH: int = 2


def convert_file(file: str) -> None:
    """
    Convert ``audiofiles/<file>.raw`` (raw PCM) to a ``audiofiles/<file>.wav`` WAV file.

    Args:
        file (str):
            Base filename (without extension) of the raw audio to convert.
    """
    log.info(f"START: convert_files: convert_file: file={file}")
    with open(f"audiofiles/{file}.raw", "rb") as fi:
        data = fi.read()

    with wave.open(f"audiofiles/{file}.wav", "w") as wf:
        wf.setnchannels(MONO)
        wf.setframerate(RATE)
        wf.setsampwidth(SAMPWIDTH)
        wf.writeframes(data)
    log.info(f"DONE: convert_files: convert_file: wrote audiofiles/{file}.wav")


if __name__ == "__main__":
    try:
        convert_file(os.getenv("ONDEWO_CSI_CONVERT_FILE", "test"))
    except Exception:
        log.exception("convert_files failed.")
        sys.exit(1)
