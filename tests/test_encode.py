import pytest
from freezegun import freeze_time
from menta import Menta, TokenData

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
        "description": "Negative timestamp",
        "key": _key,
        "nonce": _nonce,
        "timestamp": -1,
        "token": None,
        "payload": _payload,
        "raises": ValueError,
    },
    {
        "description": "Oversized timestamp",
        "key": _key,
        "nonce": _nonce,
        "timestamp": 18446744073709551616,
        "token": None,
        "payload": _payload,
        "raises": ValueError,
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
        "description": "Null payload",
        "key": _key,
        "nonce": _nonce,
        "timestamp": _timestamp,
        "token": None,
        "payload": None,
        "raises": TypeError,
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
]


@pytest.mark.parametrize("v", _vectors, ids=[v["description"] for v in _vectors])
def test_encode(v):
    key = bytes.fromhex(v["key"])
    nonce = bytes.fromhex(v["nonce"])
    payload = bytes.fromhex(v["payload"]) if v.get("payload") is not None else None
    timestamp = v["timestamp"]

    # pylint: disable=protected-access
    menta = Menta(key)
    menta._nonce = nonce

    if (exc := v.get("raises")) is not None:
        with pytest.raises(exc):
            menta.encode(TokenData(payload, timestamp))
    else:
        token = menta.encode(TokenData(payload, timestamp))
        assert token == v["token"]


@freeze_time("2012-01-01")
def test_encode_null_timestamp(menta: Menta):
    token = menta.encode(TokenData(_payload))
    assert (
        token
        == "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouIpm0M0l4ma7wMcsp79pdVbRyYktnKBhSKY_dlH2K-HWZcQ0f3IeizNAzzu7Jy5I_oPwzrjc5elZMjPW-DbRf9M"
    )


def test_encode_bad_timestamp(menta: Menta):
    with pytest.raises(TypeError):
        menta.encode(TokenData(_payload, "bad_timestamp_type"))


def test_encode_with_random_nonce(menta: Menta):
    exp_token = "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w"
    data = TokenData(bytes.fromhex(_payload), _timestamp)
    token = menta.encode(data)
    assert token == exp_token

    menta = Menta(bytes.fromhex(_key))
    # pylint: disable=protected-access
    assert menta._nonce is None

    token = menta.encode(data)
    assert token != exp_token
