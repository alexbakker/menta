import pytest
from freezegun import freeze_time
from menta import Menta, TokenData

from . import EncodeVector as Vector
from . import _key, _nonce, _payload, _timestamp

_vectors = [
    Vector(
        description="Regular timestamp",
        key=_key,
        nonce=_nonce,
        timestamp=_timestamp,
        token="v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w",
        payload=_payload,
    ),
    Vector(
        description="Zero timestamp",
        key=_key,
        nonce=_nonce,
        timestamp=0,
        token="v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouMSZcs1mvjnw1pdotOx5NwqVjptty-g_F_BvEbTf-WVfAJNvVYm__PfIUQ",
        payload=_payload,
    ),
    Vector(
        description="Negative timestamp",
        key=_key,
        nonce=_nonce,
        timestamp=-1,
        token=None,
        payload=_payload,
        raises=ValueError,
    ),
    Vector(
        description="Oversized timestamp",
        key=_key,
        nonce=_nonce,
        timestamp=18446744073709551616,
        token=None,
        payload=_payload,
        raises=ValueError,
    ),
    Vector(
        description="Max timestamp",
        key=_key,
        nonce=_nonce,
        timestamp=18446744073709551615,
        token="v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-mS8XRztmjTJmvjnw1pdotOx5NwqVjptty-g_F_BvbkQWi6ikBWaSNKrhcO7-fw",
        payload=_payload,
    ),
    Vector(
        description="Null payload",
        key=_key,
        nonce=_nonce,
        timestamp=_timestamp,
        token=None,
        payload=None,
        raises=TypeError,
    ),
    Vector(
        description="Empty payload",
        key=_key,
        nonce=_nonce,
        timestamp=_timestamp,
        token="v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuQIMuLBvKsPfNp_l4kjlkKf",
        payload="",
    ),
    Vector(
        description="Null-byte payload",
        key=_key,
        nonce=_nonce,
        timestamp=_timestamp,
        token="v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuQS1lCD9v4blLUVsxWRDNs7Hx7BMPBiDmI",
        payload="0000000000000000",
    ),
]


@pytest.mark.parametrize("v", _vectors, ids=[v.description for v in _vectors])
def test_encode(v: Vector) -> None:
    key = bytes.fromhex(v.key)
    nonce = bytes.fromhex(v.nonce)
    payload = bytes.fromhex(v.payload) if v.payload is not None else None

    # pylint: disable=protected-access
    menta = Menta(key)
    menta._nonce = nonce

    if v.raises is not None:
        with pytest.raises(v.raises):
            menta.encode(TokenData(payload, v.timestamp))  # type: ignore[arg-type]
    else:
        token = menta.encode(TokenData(payload, v.timestamp))  # type: ignore[arg-type]
        assert token == v.token


@freeze_time("2012-01-01")
def test_encode_null_timestamp(menta: Menta) -> None:
    token = menta.encode(TokenData(_payload))
    assert (
        token
        == "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouIpm0M0l4ma7wMcsp79pdVbRyYktnKBhSKY_dlH2K-HWZcQ0f3IeizNAzzu7Jy5I_oPwzrjc5elZMjPW-DbRf9M"
    )


def test_encode_bad_timestamp(menta: Menta) -> None:
    with pytest.raises(TypeError):
        menta.encode(TokenData(_payload, "bad_timestamp_type"))  # type: ignore[arg-type]


def test_encode_with_random_nonce(menta: Menta) -> None:
    exp_token = "v1:bXWGWsQYw6ipOEm0QwnCqRRQZC1v8GQ-ZtDouKbmDuRmvjnw1pdotOx5NwqVjptty-g_F_BvNfUabYqpCX-hzbON16JQ6w"
    data = TokenData(bytes.fromhex(_payload), _timestamp)
    token = menta.encode(data)
    assert token == exp_token

    menta = Menta(bytes.fromhex(_key))
    # pylint: disable=protected-access
    assert menta._nonce is None

    token = menta.encode(data)
    assert token != exp_token
