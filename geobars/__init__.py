import itertools
import subprocess
from collections.abc import Iterator, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def du(p: Path, depth: int = 1) -> dict[Path, int]:
    """Simple wrapper for Disk Usage command"""
    depth = int(depth)  # safety: ensure that it's a normal int
    if depth < 0:
        raise ValueError

    res = [
        line.split(maxsplit=1)
        for line in subprocess.check_output(
            ["/usr/bin/du", "--bytes", f"-d{depth}", str(p)], shell=False
        )
        .decode("utf-8")
        .splitlines()
    ]

    return {Path(path): int(size) for size, path in res}


def find_min(
    x: Sequence[T],
    key: None | Callable[[T]] = None,
) -> tuple[int, T]:
    key = lambda x: x[1] if key is None else key(x[1])
    return min(enumerate(iterable=x), key=key)


def pop_geometrically_dense(
    *items: tuple[T, float],
) -> Iterator[T]:
    """
    Iterativley yields points that are geometrically "close" to each other.

    The algorithm:
    1. Sorts items by their second value (time, in arbitrary units)
    2. Calculates the geometric ratio between adjacent pairs
    3. Finds the two items which are "closest" to each other (i.e., their ratio closer to 1:1 than all other ratios)
    3. Pops the left (smaller) element, repeating until two items remain


    Parameters:
        *items:
            List of tuples where the second element is used for ratio calculation
            (typically in the form of (backup_id, timestamp))

    Yields:
        Items that create the smallest geometric ratio with their neighbors,
        in the order they are removed

    Visual Example:
        ```
        >>> itr = pop_geometrically_dense([1, 3, 4, 10, 25]):

        # Initial state:
        # 1    3 4        10                  25
        # |----|-|---------|-------------------|
        #   ^
        #   | smallest ratio (3/4 = 0.75), so 3 is next

        >>> next(itr)  # = 3
        # 1      4        10                  25
        # |------|---------|-------------------|
        #

        >>> next(itr)  # = 1

        # After second iteration:
        #        4        10                  25
        # -------|---------|-------------------|

        >>> next(itr)  # = 10
        # After third iteration:
        #        4                            25
        # -------|-----------------------------|
        ```
    """
    # fmt: off

    items = sorted(items, key=lambda x: x[1])

    while len(items) > 1:
        ratios: list[float] = [
            bigger / smaller  # Geometric Ratio
            for ((_, smaller), (_, bigger))
            in itertools.pairwise(items)
        ]

        idx, _ratio = find_min(ratios)
        yield items.pop(idx)
    # fmt: on
