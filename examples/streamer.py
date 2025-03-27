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
import logging
import queue
import time
import uuid
from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    Iterator,
    Optional,
)

from ondewo.logging.logger import logger_console
from ondewo.nlu.session_pb2 import (
    InputAudioConfig,
    QueryInput,
    StreamingDetectIntentRequest,
)
from ondewo.s2t import speech_to_text_pb2
from ondewo.s2t.speech_to_text_pb2 import TranscribeStreamRequest

from ondewo.csi.conversation_pb2 import S2sStreamRequest

CHUNK: int = 8000
MONO: int = 1
RATE: int = 16000
PLAYING: bool = False
WAV_HEADER_LENGTH: int = 46
SAMPLEWIDTH: int = 2


class StreamerInInterface(metaclass=ABCMeta):
    @property
    @abstractmethod
    def mute(self) -> bool:
        pass

    @mute.setter
    def mute(self, value: bool) -> None:
        pass

    @abstractmethod
    def create_s2s_request(
        self,
        pipeline_id: str,
        session_id: Optional[str] = None,
        save_to_disk: bool = False,
        initial_intent_display_name: Optional[str] = None,
    ) -> Iterator[S2sStreamRequest]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class StreamerOutInterface(metaclass=ABCMeta):
    @abstractmethod
    def play(self, data: bytes) -> None:
        pass


class PyAudioStreamerOut(StreamerOutInterface):
    def __init__(self) -> None:
        import pyaudio

        self.CHUNK: int = CHUNK
        self.pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=22050,
            output=True,
        )

    def play(self, data: bytes) -> None:
        global PLAYING
        PLAYING = True
        self.stream.write(data[WAV_HEADER_LENGTH:])
        # self.stream.write(data)
        PLAYING = False


class PyAudioStreamerIn(StreamerInInterface):
    def __init__(self) -> None:
        import pyaudio

        self.CHUNK: int = CHUNK
        self.pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=16000,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

    @property
    def mute(self) -> bool:
        return PLAYING

    @mute.setter
    def mute(self, value: bool) -> None:
        global PLAYING
        PLAYING = value

    def close(self) -> None:
        self.stream.close()
        self.pyaudio_object.terminate()

    def create_s2s_request(
        self,
        pipeline_id: str,
        session_id: Optional[str] = None,
        save_to_disk: bool = False,
        initial_intent_display_name: Optional[str] = None,
    ) -> Iterator[S2sStreamRequest]:
        # create an initial request with session id specified
        yield S2sStreamRequest(
            pipeline_id=pipeline_id,
            session_id=session_id or str(uuid.uuid4()),
            initial_intent_display_name=initial_intent_display_name,  # type: ignore[arg-type]
            # In the proto its optional
        )

        count = 0
        data_save = bytes()
        if save_to_disk:
            f = open(f"record_{session_id}.raw", "wb")

        global PLAYING
        while True:  # not self.stop.done():

            if PLAYING:
                print("PLAYING")
                time.sleep(0.5)
                self.stream.stop_stream()
                continue

            self.stream.start_stream()
            count += 1
            data: bytes = self.stream.read(CHUNK)  # type: ignore
            data_save += data
            if len(data_save) < RATE:
                continue
            yield S2sStreamRequest(audio=data_save)
            if save_to_disk:
                f.write(data_save)
            data_save = bytes()
            time.sleep(0.1)

        yield S2sStreamRequest(end_of_stream=True)

    def create_pyaudio_streaming_request(self, pipeline_id: str) -> Iterator[TranscribeStreamRequest]:
        while True:
            chunk: bytes = self.stream.read(CHUNK)
            logging.info(f"Sending {len(chunk)} bytes")
            yield TranscribeStreamRequest(
                audio_chunk=chunk,
                s2t_pipeline_id=pipeline_id,
                spelling_correction=False,
                ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                end_of_stream=False,
            )
            time.sleep(0.1)


class PySoundIoStreamerOut(StreamerOutInterface):

    def __init__(self, device_id: Optional[int] = None) -> None:
        import pysoundio

        self.responses: queue.Queue = queue.Queue()
        # This is typically a single utterance from TTS
        self.response: Optional[bytes] = None
        self.idx: int = 0
        self.CHUNK: int = CHUNK
        self.pysoundio_object: pysoundio.PySoundIo = pysoundio.PySoundIo(backend=None)
        self.pysoundio_object.start_output_stream(
            device_id=device_id,
            channels=MONO,
            sample_rate=22050,
            block_size=CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            write_callback=self.callback,
        )

    def callback(self, data: list, length: int) -> None:
        if self.response is not None:
            # if we are currently playing a response
            if self.idx <= len(self.response):
                # if the response is still being played: calculate the length in bytes, overwrite the output
                # data with the portion of the response, increase the index and return
                num_bytes = length * SAMPLEWIDTH * MONO
                data[:] = self.response[self.idx: self.idx + num_bytes]  # noqa:
                self.idx += num_bytes
                return

            # if the whole response was played: remove the response and set task done in the response queue
            self.response = None
            self.responses.task_done()
            logger_console.debug("done playing")

        if not self.responses.empty():
            # if there is a response to play, get get it from the queue and reset the index
            self.response = self.responses.get()
            self.idx = WAV_HEADER_LENGTH
            logger_console.debug("start playing")

    def play(self, data: bytes) -> None:
        self.responses.put(data)
        logger_console.debug(f"output {len(data)} bytes")
        self.responses.join()


class PySoundIoStreamerIn(StreamerInInterface):
    @property
    def mute(self) -> bool:
        return self._mute

    @mute.setter
    def mute(self, value: bool) -> None:
        self._mute = value

    def __init__(self, device_id: Optional[int] = None) -> None:
        import pysoundio

        logging.debug("Initializing PySoundIo streamer")

        self.mute = False
        self.buffer: queue.Queue = queue.Queue(maxsize=CHUNK * 50)
        logging.info("Starting stream")
        # start recording
        self.pysoundio_object: pysoundio.PySoundIo = pysoundio.PySoundIo(backend=None)
        self.pysoundio_object.start_input_stream(
            device_id=device_id,
            channels=MONO,
            sample_rate=RATE,
            block_size=CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            read_callback=self.callback,
        )
        logger_console.debug("Streamer initialized")

    def callback(self, data: bytes, length: int) -> None:
        if self.mute:
            # logger_console.debug(f'dropping {len(data)} bytes, {length} samples')
            return
        # logger_console.debug(f'input {len(data)} bytes')
        self.buffer.put(data)

    def close(self) -> None:
        pass

    def create_s2s_request(
        self,
        pipeline_id: str,
        session_id: Optional[str] = None,
        save_to_disk: bool = False,
        initial_intent_display_name: Optional[str] = None,
    ) -> Iterator[S2sStreamRequest]:
        # create an initial request with session id specified
        yield S2sStreamRequest(
            pipeline_id=pipeline_id,
            session_id=session_id or str(uuid.uuid4()),
            initial_intent_display_name=initial_intent_display_name,  # type: ignore[arg-type]
            # In the proto its optional
        )

        if save_to_disk:
            f = open(f"record_{session_id}.raw", "wb")

        data_save = bytes()

        while True:
            data: bytes = self.buffer.get()

            data_save += data
            if len(data_save) < RATE:
                continue
            yield S2sStreamRequest(audio=data_save)
            if save_to_disk:
                f.write(data_save)
            data_save = bytes()
            time.sleep(0.1)

    def create_intent_request(
        self, cai_project: str, cai_session: str
    ) -> Iterator[StreamingDetectIntentRequest]:
        count = 0
        data_save = bytes()
        while True:  # not self.stop.done():
            count += 1
            data: bytes = self.buffer.get()
            data_save += data
            if len(data_save) < RATE:
                continue
            logging.info(f"Sending {len(data_save)} bytes")
            yield StreamingDetectIntentRequest(
                input_audio=data_save,
                session=f"projects/{cai_project}/agent/sessions/{cai_session}",
                query_input=QueryInput(
                    audio_config=InputAudioConfig(
                        # language_code='en',
                        language_code="de",
                    )
                ),
            )
            data_save = bytes()
            time.sleep(0.1)

    def create_pysoundio_streaming_request(
        self, pipeline_id: str
    ) -> Iterator[speech_to_text_pb2.TranscribeStreamRequest]:

        count = 0
        data_save = bytes()
        while count < 100:  # not self.stop.done():
            count += 1
            data: bytes = self.buffer.get()
            data_save += data
            if len(data_save) < RATE:
                continue
            logging.info(f"Sending {len(data_save)} bytes")
            yield TranscribeStreamRequest(
                audio_chunk=data_save,
                s2t_pipeline_id=pipeline_id,
                spelling_correction=False,
                ctc_decoding=speech_to_text_pb2.CTCDecoding.BEAM_SEARCH_WITH_LM,
                end_of_stream=False,
            )
            data_save = bytes()
            time.sleep(0.1)
