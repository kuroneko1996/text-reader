import typing
from dataclasses import dataclass


@dataclass
class Config:
    current_source: typing.Literal["local", "edgetts"]
    voices: dict[str, list[str]]
    tts_url: str
