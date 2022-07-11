from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar, overload

__version__: tuple[int, int, int]

_K = TypeVar("_K")

_V1 = TypeVar("_V1")
_V2 = TypeVar("_V2")
_V3 = TypeVar("_V3")

@overload
def dict_zip() -> Iterator:
    """dict_zip(d1, d2, ...) -> (k, v1, v2), ... iterate over corresponding key and values."""
    ...

@overload
def dict_zip(
    d1: dict[_K, _V1],
) -> Iterator[tuple[_K, _V1]]: ...
@overload
def dict_zip(
    d1: dict[_K, _V1],
    d2: dict[_K, _V2],
) -> Iterator[tuple[_K, _V1, _V2]]: ...
@overload
def dict_zip(
    d1: dict[_K, _V1],
    d2: dict[_K, _V2],
    d3: dict[_K, _V3],
) -> Iterator[tuple[_K, _V1, _V2, _V3]]: ...
