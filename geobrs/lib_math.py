import datetime
import itertools
from collections import namedtuple
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Callable, SupportsRichComparisonT, TypeVar


from pydantic import ByteSize

from geobrs import config
from geobrs.byte_count import ByteCount

T = TypeVar("T")


class Backup(namedtuple):
    path: Path
    size: ByteSize
    date: datetime


def find_min(
    x: Sequence[T],
    key: None | Callable[[T], SupportsRichComparisonT] = None,
) -> tuple[int, T]:
    key = lambda x: x[1] if key is None else key(x[1])
    return min(enumerate(iterable=x), key=key)


# from dataclass_wizard import TOMLWizard


def pop_geometrically_dense(
    *items: T, key: Callable[[T], SupportsRichComparisonT] = lambda x: x
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




def solve(
    backups: list[Backup],
    # keep_newest_bytes: ByteCount,
    # keep_newest_count: int,
    # keep_newest_mins: datetime.timedelta,
    always_keep_newest: config.CSA,
    keep_dynamic_size: ByteSize,
    keep_dynamic_count: ByteSize,
    always_discard: config.CSA,
) -> None:
    unassigned: list[Backup] = []
    keep: list[Backup] = []
    delete: list[Backup] = []

    backups.sort(key=lambda x: x.date)



    # keep_newest
    keep,unassigned = backups[:always_keep_newest.count], backups[always_keep_newest.count:]
    keep_before = datetime.datetime() - always_keep_newest.age
    too_old = True

    sum_bytes_keep = sum(b.size for b in keep)
    sum_bytes_unassigned = sum(b.size for b in unassigned)
    sum_bytes_delete = sum(b.size for b in delete)

    while sum_bytes_keep > always_keep_newest.size and too_old:
        b = unassigned.pop(0)

        sum_bytes_keep += b.size
        keep.append(b)

        if too_old and unassigned[0].date > keep_before:
            too_old = False


    sum_bytes_keep = sum(b.size for b in keep)
    sum_bytes_unassigned = sum(b.size for b in unassigned)
    sum_bytes_delete = sum(b.size for b in delete)

    while len(unassigned) + len(keep) > keep_dynamic.count and sum_bytes_unassigned + sum_bytes_keep < keep_dynamic.size:






    for backup in sorted(backups,key=lambda b:b.date):



# conditions to keep all remaining backups

# conditions to keep this backup immediatley


# suppose you have a config with the following properties
# keep_newest_bytes
# keep_newest.count
# keep_newest_mins

# keep_at_least_size_bytes
# keep_at_least_count

# discard_over_size_bytes
# discard_over_count
# discard_older_than_mins
#
# you are given an ordered list of backup NamedTuples, with "age_in_mins", and "size_in_bytes" params.
#
# you are to return an "acceptable" list of backups to delete
# a deletion list is acceptable if and only if:
# - it contains no backups that match the keep_newest rules
# - id

# you are also given a "preference order", which indicates in what order the user would prefer you to dele
