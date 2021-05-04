![Logo](https://raw.githubusercontent.com/ondewo/ondewo-logos/master/github/ondewo_logo_github_2.png)

ONDEWO-CSI Client Library
======================

This library facilitates the interaction between a user and an ONDEWO-CSI server instance. 

It is structured around a series of python files generated from protobuf files. These protobuf files specify the details of the interface, and can be used to generate code in 10+ high-level languages. They are found in the [apis submodule](./ondewo-csi-api).

Python Installation
-------------------

```bash
git clone git@github.com:ondewo/ondewo-csi-client-python.git
cd ondewo-csi-client-python
pip install -r requirements.txt
```

Let's Get Started! (WIP)
------------------
Import your programming interface:
```bash
ls ondewo
```

Get a suitable example:
```bash
ls examples
```

Examples
------------------

To use the example script, you need pyaudio and/or pysoundio installed.

```pyaudio installation
sudo apt install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt install -y ffmpeg libav-tools

pip install pyaudio
```

```pysoundio installation
sudo apt install -y libsoundio-dev

pip install pysoundio
```
