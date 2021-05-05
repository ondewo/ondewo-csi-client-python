import logging
import queue
import time
import uuid
from typing import Iterator, Optional

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
PLAYING: bool = False
WAV_HEADER_LENGTH: int = 46


class PyAudioStreamerOut:
    def __init__(self) -> None:
        import pyaudio

        self.CHUNK: int = CHUNK
        self.pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream = self.pyaudio_object.open(
            channels=1,
            format=pyaudio.paInt16,
            rate=22000,
            output=True,
        )

    def play(self, data):
        global PLAYING
        PLAYING = True
        self.stream.write(data[WAV_HEADER_LENGTH:])
        # self.stream.write(data)
        PLAYING = False


class PyAudioStreamerIn:
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

    def close(self) -> None:
        self.stream.close()
        self.pyaudio_object.terminate()

    def create_s2s_request(
        self,
        pipeline_id: str,
        session_id: Optional[str] = None,
        save_to_disk=False,
    ) -> Iterator[S2sStreamRequest]:
        # create an initial request with session id specified
        yield S2sStreamRequest(pipeline_id=pipeline_id, session_id=session_id)

        count = 0
        data_save = bytes()
        if save_to_disk:
            f = open(f"audiofiles/record_{session_id}.raw", "wb")

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


class PySoundIoStreamerOut:
    def __init__(self) -> None:
        import pysoundio

        self.responses: queue.Queue = queue.Queue()
        self.stream = None
        self.idx = 0
        self.CHUNK: int = CHUNK
        self.pysoundio_object: pysoundio.PySoundIo = pysoundio.PySoundIo(backend=None)
        self.pysoundio_object.start_output_stream(
            device_id=None,
            channels=MONO,
            sample_rate=22000,
            block_size=CHUNK,
            dtype=pysoundio.SoundIoFormatS16LE,
            write_callback=self.callback,
        )

    def callback(self, data, length):
        global PLAYING
        if self.stream and self.idx > len(self.stream):
            PLAYING = False
            self.idx = WAV_HEADER_LENGTH
            self.stream = None
        if self.stream is not None:
            num_bytes = length * 2 * MONO
            data[:] = self.stream[self.idx : self.idx + num_bytes]  # noqa:
            self.idx += num_bytes
        elif not self.responses.empty():
            PLAYING = True
            self.stream = self.responses.get()
            self.idx = WAV_HEADER_LENGTH

    def play(self, data):
        self.responses.put(data)


class PySoundIoStreamerIn:
    def __init__(self) -> None:
        import pysoundio

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
        self,
        pipeline_id: str,
        session_id: Optional[str] = None,
        save_to_disk: bool = False,
    ) -> Iterator[S2sStreamRequest]:
        global PLAYING
        # create an initial request with session id specified
        yield S2sStreamRequest(pipeline_id=pipeline_id, session_id=session_id or str(uuid.uuid4()))

        if save_to_disk:
            f = open(f"audiofiles/record_{session_id}.raw", "wb")

        count = 0
        data_save = bytes()

        while True:  # not self.stop.done():
            if PLAYING:
                # data : bytes = bytes()
                time.sleep(0.7)
                continue

            count += 1
            data: bytes = self.buffer.get()  # type: ignore
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

    def create_pysoundio_streaming_request(
        self, pipeline_id: str
    ) -> Iterator[speech_to_text_pb2.TranscribeStreamRequest]:

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
