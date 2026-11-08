from enum import Enum


class AppSource(Enum):
    Local = 0
    EdgeTTS = 1


CURRENT_SOURCE = AppSource.Local
LOCAL_TTS_URL = "http://localhost:8000/tts"

VOICES = (
    [
        "alba",
        "anna",
        "bill_boerst",
    ],
    [
        "en-GB-SoniaNeural",
        "en-US-ChristopherNeural",
        "en-AU-NatashaNeural",
        "ru-RU-DmitryNeural",
        "ru-RU-SvetlanaNeural",
    ],
)
