import contextlib
from itertools import count
from typing import Final, Literal, LiteralString, Self

# fmt: off
prefixes: Final[dict[LiteralString, int]]  = {
    "byte": 1, "bytes": 1,
    "kib": 1024**1,  "kibibyte":  1024**1,  "kibibytes":  1024**1,
    "mib": 1024**2,  "mebibyte":  1024**2,  "mebibytes":  1024**2,
    "gib": 1024**3,  "gibibyte":  1024**3,  "gibibytes":  1024**3,
    "tib": 1024**4,  "tebibyte":  1024**4,  "tebibytes":  1024**4,
    "pib": 1024**5,  "pebibyte":  1024**5,  "pebibytes":  1024**5,
    "eib": 1024**6,  "exbibyte":  1024**6,  "exbibytes":  1024**6,
    "zib": 1024**7,  "zebibyte":  1024**7,  "zebibytes":  1024**7,
    "yib": 1024**8,  "yobibyte":  1024**8,  "yobibytes":  1024**8,
    "rib": 1024**9,  "robibyte":  1024**9,  "robibytes":  1024**9,
    "qib": 1024**10, "quebibyte": 1024**10, "quebibytes": 1024**10,

    "kb": 1000**1,  "kilobyte":   1000**1,  "k": 1000**1,  "kilobytes":   1000**1,
    "mb": 1000**2,  "megabyte":   1000**2,  "m": 1000**2,  "megabytes":   1000**2,
    "gb": 1000**3,  "gigabyte":   1000**3,  "g": 1000**3,  "gigabytes":   1000**3,
    "tb": 1000**4,  "terabyte":   1000**4,  "t": 1000**4,  "terabytes":   1000**4,
    "pb": 1000**5,  "petabyte":   1000**5,  "p": 1000**5,  "petabytes":   1000**5,
    "eb": 1000**6,  "exabyte":    1000**6,  "e": 1000**6,  "exabytes":    1000**6,
    "zb": 1000**7,  "zettabyte":  1000**7,  "z": 1000**7,  "zettabytes":  1000**7,
    "yb": 1000**8,  "yottabyte":  1000**8,  "y": 1000**8,  "yottabytes":  1000**8,
    "rb": 1000**9,  "ronnabyte":  1000**9,  "r": 1000**9,  "ronnabytes":  1000**9,
    "qb": 1000**10, "quettabyte": 1000**10, "q": 1000**10, "quettabytes": 1000**10,
}

# fmt: on
first_letters: dict[Literal["k", "m", "g", "t", "p", "e", "z", "y", "r", "q"], int] = {
    c: i + 1 for i, c in enumerate("kmgtpezyrq")
}


class FormatError(ValueError): ...


class ByteCount(int):
    def get_magnitude_IEC(self) -> int:
        for i in count(1):
            if self > (1024**i):
                continue
            return i - 1

    def get_magnitude_SI(self) -> int:
        for i in count(1):
            if self > (1000**i):
                continue
            return i - 1

    def __repr__(self) -> str:
        classname: str = self.__class__.__name__

        magnitude: int = self.get_magnitude_IEC()
        prefixes = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi", "Ri", "Qi"]

        if magnitude in range(len(prefixes)):
            value = self / (1024**magnitude)
            return f"{classname}({value:.2f} {prefixes[magnitude]}B)"
        return f"{classname} ({int(self)} bytes)"

    @classmethod
    def from_str(cls, s: str):
        with contextlib.suppress(ValueError):
            return cls(int(s))

        m: list[str] = s.strip().lower().split()
        if len(m) != 2:
            raise FormatError
        scalar, suffix = m

        try:
            return cls(int(scalar) * prefixes[suffix])
        except (KeyError, ValueError) as k:
            raise FormatError from k

    def __new__(cls, s: str | int) -> Self:
        match s:
            case str():
                return cls.from_str(s)
            case int() | ByteCount():
                return cls(s)
            case _:
                raise TypeError
