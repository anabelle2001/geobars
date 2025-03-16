import io
from datetime import timedelta
from typing import NamedTuple, Self

import pytimeparse
import tomllib

from geobrs.byte_count import ByteCount


class CSA(NamedTuple):
    count: int | None
    size: ByteCount | None
    age: timedelta | None

    def __init__(
        self,
        count: int | None = None,
        size: ByteCount | int | str | None = None,
        age: timedelta | str | None = None,
    ) -> None:
        match count:

            case int() | None:
                self.count = count
            case _:
                raise TypeError("`count` must be int or none")

        match size:
            case str() | int():
                self.size = ByteCount(size)
            case ByteCount() | None:
                self.size = size
            case _:
                raise TypeError

        match age:
            case str():
                self.age = timedelta(seconds=pytimeparse.parse(age))
            case timedelta() | None:
                self.age = age
            case _:
                raise TypeError


class Config:
    @classmethod
    def load(cls, f: io.BytesIO) -> Self:
        return cls(*tomllib.load(f))

    def __init__(
        self,
        select: str,
        keep: CSA | dict | None = None,
        discard: CSA | dict | None = None,
    ) -> None:
        match select:
            case str():
                self.select: str = select
            case _:
                raise TypeError("`select` must be a glob")

        match keep:
            case CSA() | None:
                self.keep: CSA | None = keep
            case dict():
                self.keep = CSA(**keep)
            case _:
                raise TypeError("`keep` must be a map/config/dict or None")

        match discard:
            case CSA() | None:
                self.discard: CSA | None = discard
            case dict():
                self.discard = CSA(**discard)
            case _:
                raise TypeError("`discard` must be a map/config/dict or None")
