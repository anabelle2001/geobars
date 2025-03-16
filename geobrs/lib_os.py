import subprocess
from pathlib import Path


def du(p: Path, depth: int = 1) -> dict[Path, int]:
    """Simple wrapper for Disk Usage command"""
    depth = int(depth)  # safety: ensure that it's a normal int
    if depth < 0:
        raise ValueError

    res = [
        line.split(maxsplit=1)
        for line in subprocess.check_output(  # noqa: S603
            ["/usr/bin/du", "--bytes", f"-d{depth}", str(p)], shell=False
        )
        .decode("utf-8")
        .splitlines()
    ]

    return {Path(path): int(size) for size, path in res}
