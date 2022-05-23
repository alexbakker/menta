from menta import Menta, TokenData
from pytest_benchmark.fixture import BenchmarkFixture  # type: ignore

from . import _payload


def test_encode_perf(benchmark: BenchmarkFixture) -> None:
    menta = Menta.generate()
    benchmark(lambda: menta.encode(TokenData(_payload)))


def test_decode_perf(benchmark: BenchmarkFixture) -> None:
    menta = Menta.generate()
    token = menta.encode(TokenData(_payload))
    benchmark(lambda: menta.decode(token))
