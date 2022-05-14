import os

from menta import Menta


def test_sanity():
    key = os.urandom(Menta.KEY_SIZE)
    menta = Menta(key)
    assert menta.key == key

    menta = menta.generate()
    menta2 = menta.generate()
    assert menta.key != menta2.key
