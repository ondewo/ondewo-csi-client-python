import logging
import queue
import time
from typing import Iterator

import pyaudio
import pysoundio
from ondewo.logging.logger import logger_console as stream_logger
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


class PyAudioStreamer:

    def __init__(self) -> None:
        self.CHUNK: int = CHUNK
        self.pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=16000,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

    def close(self) -> None:
        self.stream.close()
        self.pyaudio_object.terminate()

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


class PysoundIOStreamer:

    def __init__(self) -> object:
        logging.debug("Initializing PySoundIo streamer")

        self.buffer: queue.Queue = queue.Queue(maxsize=CHUNK * 50)
        logging.info("Starting stream")
        # start recording
        self.pysoundio_object: pysoundio.PySoundIo = pysoundio.PySoundIo(backend=None)
        self.pysoundio_object.start_input_stream(
            device_id=None,
            channels=MONO,
            sample_rate=RATE,
            block_size=CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            read_callback=self.callback,
        )
        stream_logger.debug("Streamer initialized")

    def callback(self, data: bytes, length: int) -> None:
        self.buffer.put(data)

    def close(self):
        pass

    def create_s2s_request(
            session_id: str = "streaming-test-pizza"
    ) -> Iterator[S2sStreamRequest]:
        # create an initial request with session id specified
        yield S2sStreamRequest(session_id=session_id)

        count = 0
        data_save = bytes()
        while True:  # not self.stop.done():
            count += 1
            data: bytes = self.buffer.get()  # type: ignore
            data_save += data
            if len(data_save) < RATE:
                continue
            yield S2sStreamRequest(audio=data_save)

        yield S2sStreamRequest(end_of_stream=True)

    def create_intent_request(self, cai_project: str,
                              cai_session: str) -> Iterator[StreamingDetectIntentRequest]:
        count = 0
        data_save = bytes()
        while True:  # not self.stop.done():
            count += 1
            data: bytes = self.buffer.get()  # type: ignore
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

    def create_pysoundio_streaming_request(self, pipeline_id: str) -> Iterator[
        speech_to_text_pb2.TranscribeStreamRequest]:

        count = 0
        data_save = bytes()
        while count < 100:  # not self.stop.done():
            count += 1
            data: bytes = self.buffer.get()  # type: ignore
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