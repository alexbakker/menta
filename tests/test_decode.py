import time

import pytest
from menta import Menta, errors, TokenData

from . import _key, _nonce, _payload, _timestamp

_vectors = [
    {
        "description": "Regular timestamp",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
    },
    {
        "description": "Zero timestamp",
        "key": _key,
        "nonce": _nonce,
        "timestamp": 0,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouMSZcs1mvjnw1pdotOx5NwqVjptty-g_F_BvEbTf-WVfAJNvVYm__PfIUQ",
        "payload": _payload,
    },
    {
        "description": "Max timestamp",
        "key": _key,
        "nonce": _nonce,
        "timestamp": 18446744073709551615,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-mS8XRztmjTJmvjnw1pdotOx5NwqVjptty-g_F_BvbkQWi6ikBWaSNKrhcO7-fw",
        "payload": _payload,
    },
    {
        "description": "Empty payload",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuQIMuLBvKsPfNp_l4kjlkKf",
        "payload": "",
    },
    {
        "description": "Null-byte payload",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuQS1lCD9v4blLUVsxWRDNs7Hx7BMPBiDmI",
        "payload": "0000000000000000",
    },
    {
        "description": "Bad header",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "d1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.BadVersionError,
    },
    {
        "description": "Bad version",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v2:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.BadVersionError,
    },
    {
        "description": "Bad format (extra colon)",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1::bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.BadFormatError,
    },
    {
        "description": "Random data",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "1db82fc6c408382d1ce85d8d73784a4e9f6048b631e20f85afd7cb59d2261050",
        "payload": _payload,
        "raises": errors.BadFormatError,
    },
    {
        "description": "Too short",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-bYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.BadFormatError,
    },
    {
        "description": "Bad key",
        "key": "c359a687fe179a393b073747f9e81704b08e1a127f9b5d05c01f4f37a200d4bd",
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.DecryptError,
    },
    {
        "description": "Corrupt nonce",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWdQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.DecryptError,
    },
    {
        "description": "Corrupt payload",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWdQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1peotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "raises": errors.DecryptError,
    },
    {
        "description": "Corrupt tag",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hebON16JQ6w",
        "payload": _payload,
        "raises": errors.DecryptError,
    },
    {
        "description": "Not expired",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "ttl": (int(time.time()) - _timestamp) + 60,
    },
    {
        "description": "Expired",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        "payload": _payload,
        "ttl": (int(time.time()) - _timestamp) - 60,
        "raises": errors.ExpiredError,
    },
]


@pytest.mark.parametrize("v", _vectors, ids=[v["description"] for v in _vectors])
def test_decode(v):
    key = bytes.fromhex(v["key"])
    nonce = bytes.fromhex(v["nonce"])
    payload = bytes.fromhex(v["payload"])
    timestamp = v["timestamp"]
    ttl = v.get("ttl")

    # pylint: disable=protected-access
    menta = Menta(key)
    menta._nonce = nonce

    if (exc := v.get("raises")) is not None:
        with pytest.raises(exc):
            menta.decode(v["token"], ttl)
    else:
        data = menta.decode(v["token"], ttl)
        assert data.payload == payload
        assert data.timestamp == timestamp


def test_decode_bad_types(menta: Menta):
    with pytest.raises(TypeError):
        menta.decode(b"bad_token_type")
    with pytest.raises(TypeError):
        menta.decode("", "bad_timestamp_type")

def test_decode_future_timestamp(menta: Menta):
    token = menta.encode(TokenData(_payload, timestamp=int(time.time()) + 60))
    menta.decode(token, ttl=10)

def test_decode_negative_ttl(menta: Menta):
    token = menta.encode(TokenData(_payload))
    with pytest.raises(ValueError):
        menta.decode(token, ttl=-1)
