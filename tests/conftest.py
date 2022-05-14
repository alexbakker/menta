import pytest
from menta import Menta

from . import _key, _nonce


@pytest.fixture()
def menta() -> Menta:
    m = Menta(bytes.fromhex(_key))
    # pylint: disable=protected-access
    m._nonce = bytes.fromhex(_nonce)
    return m
