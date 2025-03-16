# SPDX-License-Identifier: MPL-2.0

import pathlib
from os import name, stat_result

import rich
import typer

from geobrs.config import Config
from geobrs.lib_math import pop_geometrically_dense
from geobrs.lib_os import du


@typer.Typer
def main(
    path: pathlib.Path | None,
    dry: bool = False,
) -> None:
    path = path or pathlib.cwd()

    if path.is_file():
        if path.name != "geobrs.toml" or not path.exists():
            raise OSError
        path = path.parent

    if not path.is_dir():
        raise OSError

    cfg: Config = Config.load((path / "geobrs.toml").read_bytes())

    def can_cull(p: pathlib.Path) -> bool:
        stat: stat_result = p.stat(follow_symlinks=False)
        if not p.is_file() and not p.is_dir():
            return False
        if not stat.st_birthtime:
            ...

    for f in path.iterdir():
        x = f.stat()
        if not isinstance(x, stat_result):
            raise OSError
        x.st_birthtime
