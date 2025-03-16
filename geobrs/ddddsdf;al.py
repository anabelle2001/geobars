import datetime
from collections import namedtuple
from pathlib import Path

from geobrs.byte_count import ByteCount
from geobrs.lib_math import pop_geometrically_dense


class Backup(namedtuple):
    path: Path
    size: ByteCount
    date: datetime


class CSA:
    """Count, Size, Age criteria"""

    count: int | None
    size: ByteCount | None
    age: datetime.timedelta | None


class RetentionPolicy:
    always_keep_newest: CSA
    keep_dynamic: CSA
    always_discard: CSA


def solve(
    backups: list[Backup],
    keep_first: CSA,
    keep_dynamic: CSA,
    discard_last: CSA,
) -> tuple[list[Backup], list[Backup]]:
    """
    Determines which backups to keep and which to delete based on the specified retention policy.

    Args:
        backups: List of backup objects to evaluate
        retention_policy: Configuration containing all retention rules

    Returns:
        tuple of (backups_to_keep, backups_to_delete)
    """

    keep_first.age |= datetime.timedelta(seconds=0)
    keep_first.count |= 0
    keep_first.size |= ByteCount(0)
    discard_last.age |= datetime.timedelta(days=999999999)  # max supported value
    # Extract policy parameters for clarity

    # Sort backups from newest to oldest
    sorted_backups = sorted(backups, key=lambda b: b.date, reverse=True)

    # Initialize our categorized lists
    keep: list[Backup] = []
    delete: list[Backup] = []
    unassigned: list[Backup] = []

    # Step 1: Apply always_keep_newest criteria
    current_date = datetime.datetime.now()
    keep_age_threshold = current_date - keep_first.age

    for backup in sorted_backups:
        if (
            len(keep) < keep_first.count
            or backup.date < keep_age_threshold
            or sum(b.size for b in keep) < keep_first.size
        ):
            keep.append(backup)
        else:
            unassigned.append(backup)

    # Step 2: Apply always_discard criteria
    discard_age_threshold = current_date - discard_last.age
    still_unassigned = []

    for backup in unassigned:
        if (
            backup.date < discard_age_threshold
            or sum(b.size for b in keep + still_unassigned) + backup.size
            > discard_last.size
            or len(keep) + len(still_unassigned) >= discard_last.count
        ):
            delete.append(backup)
        else:
            still_unassigned.append(backup)

    unassigned = still_unassigned

    if len(unassigned) == 0:
        return keep, delete

    # Step 3: Apply dynamic criteria to remaining unassigned backups
    backup_with_timestamp = [(b, b.date.timestamp()) for b in unassigned]

    remaining_count = keep_dynamic.count - len(keep)
    remaining_size = keep_dynamic.size - sum(b.size for b in keep)

    geometrically_dense_order = list(pop_geometrically_dense(*backup_with_timestamp))

    current_size = 0
    count = 0

    for backup, _ in geometrically_dense_order:
        if count >= remaining_count or current_size + backup.size > remaining_size:
            delete.append(backup)
        else:
            keep.append(backup)
            current_size += backup.size
            count += 1

    return keep, delete
