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
