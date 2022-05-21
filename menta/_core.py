from __future__ import annotations

import os
import struct
import time
from dataclasses import dataclass
from typing import Final, Optional, Union

import nacl.exceptions
from nacl.secret import Aead
from nacl.utils import random

from . import errors
from ._utils import b64decode, b64encode


@dataclass
class TokenData:
    payload: Union[bytes, str]
    timestamp: Optional[int] = None


class Menta:
    SEP: Final[str] = ":"
    """The character used to separate the version indicator from the
    ciphertext."""

    VERSION: Final[str] = "v1"
    """The version indicator."""

    KEY_SIZE: Final[int] = Aead.KEY_SIZE
    """Size of the key used for encryption, in bytes."""

    TIMESTAMP_SIZE: Final[int] = 8
    """Size of the timestamp in bytes."""

    def __init__(self, key: bytes):
        self._key = key
        self._aead = Aead(key)

        self._nonce = None
        """NEVER assign anything but None to this variable. In tests, this
        variable is used to bypass random nonce generation."""

    @property
    def key(self) -> bytes:
        """Returns the raw key that is used for encryption."""
        return self._key

    @classmethod
    def generate(cls) -> Menta:
        """
        Creates a new Menta instance using a freshly generated key obtained from
        os.urandom.

        Returns:
            Menta: A Menta instance.
        """
        key = os.urandom(cls.KEY_SIZE)
        return Menta(key)

    def encode(self, data: TokenData) -> str:
        """
        Encodes the given data into a Menta token.

        Args:
            token (TokenData): The data to encode in the token. If the given
            timestamp is None, the current system time is used.

        Returns:
            str: An encoded Menta token.

        Raises:
            TypeError: Invalid type of arguments.
        """
        payload = data.payload
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        if not isinstance(payload, bytes):
            raise TypeError("Payload must be of type str or bytes")

        timestamp = data.timestamp
        if timestamp is None:
            timestamp = int(time.time())
        if not isinstance(timestamp, int):
            raise TypeError("Timestamp must be of type int")

        # In tests, we set self._nonce to a static value. NEVER do this when
        # actually using Menta.
        nonce = self._nonce
        if nonce is None:
            nonce = random(self._aead.NONCE_SIZE)

        try:
            t = struct.pack(">Q", timestamp)
        except struct.error as e:
            raise ValueError(f"Bad timestamp: {timestamp}") from e

        aad = self._get_aad(self.VERSION.encode("utf-8"), nonce)
        msg = self._aead.encrypt(t + payload, aad, nonce)
        return f"{self.VERSION}:{b64encode(nonce + msg.ciphertext).decode('utf-8')}"

    def decode(self, token: str, ttl: int = None) -> TokenData:
        """
        Decodes the given Menta token. All types of exceptions that this method
        can throw are subclasses of `MentaError`, so you can catch that
        exception type to catch any decode errors.

        Args:
            token (str): The Menta token to decode.
            ttl (:obj:`int`, optional): Time to live. If the timestamp encoded
            in the token indicates that the token has exceeded the TTL, an
            exception is thrown.

        Returns:
            TokenData: A decoded Menta token.

        Raises:
            TypeError: Invalid type of arguments.
            DecryptError: Decryption failed.
            BadFormatError: Token is incorrectly formatted.
            BadVersionError: Token is using an unsupported version.
            ExpiredError: The token has expired.
        """
        if not isinstance(token, str):
            raise TypeError("Token must be of type str")
        if ttl is not None:
            if not isinstance(ttl, int):
                raise TypeError("TTL must be of type int")
            if ttl < 0:
                raise ValueError("TTL must be larger than zero")

        parts = token.split(self.SEP)
        if len(parts) != 2:
            raise errors.BadFormatError("Bad token format")

        version, body = parts
        if version != self.VERSION:
            raise errors.BadVersionError(f"Bad version: {version}")

        body_bytes = b64decode(body.encode("utf-8"))
        if len(body_bytes) < self._aead.NONCE_SIZE + self._aead.MACBYTES + self.TIMESTAMP_SIZE:
            raise errors.BadFormatError("Bad token format")

        nonce = body_bytes[: self._aead.NONCE_SIZE]
        aad = self._get_aad(version.encode("utf-8"), nonce)
        ciphertext = body_bytes[self._aead.NONCE_SIZE :]

        try:
            body = self._aead.decrypt(ciphertext, aad, nonce)
        except nacl.exceptions.CryptoError as e:
            raise errors.DecryptError("Unable to decrypt token") from e

        timestamp = struct.unpack(">Q", body[: self.TIMESTAMP_SIZE])[0]
        if ttl is not None and (time.time() - timestamp) > ttl:
            raise errors.ExpiredError("Token has expired")

        payload = body[self.TIMESTAMP_SIZE :]
        return TokenData(payload, timestamp)

    @classmethod
    def _get_aad(cls, version: bytes, nonce: bytes) -> bytes:
        return version + cls.SEP.encode("utf-8") + nonce
