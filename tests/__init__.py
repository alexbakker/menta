from dataclasses import dataclass
from typing import Optional, Type

_key = "52fb6326509b448b9051c36ee8b83c69a05acac16f1e4d9d2d7a2c59c63501c6"
_nonce = "6d75865ac418c3a8a93849b44309c2a91450642d6ff0643e"
_payload = "7468697320697320612074657374207061796c6f6164"
_timestamp = 1652522025


@dataclass
class EncodeVector:
    description: str
    key: str
    nonce: str
    timestamp: int
    token: Optional[str]
    payload: Optional[str]
    raises: Optional[Type[Exception]] = None


@dataclass
class DecodeVector:
    description: str
    key: str
    nonce: str
    timestamp: int
    token: str
    payload: Optional[str]
    ttl: Optional[int] = None
    raises: Optional[Type[Exception]] = None
