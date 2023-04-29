from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Union


class Filesystem:
    folder: Path

    def __init__(self, folder: str):
        # We need to use resolve here to get an absolute path
        self.folder = Path(folder).resolve()

    def get_path(self, fullpath: Path) -> str:
        # We need to use resolve here to prevent path traversing
        path = str(Path(fullpath).resolve().relative_to(self.folder))
        assert path != "."
        assert path != ""
        return path

    def get_fullpath(
        self, *paths: Optional[str], deduplicate: Optional[Union[bool, str]] = None
    ) -> Path:
        # We need to use resolve here to get normalized path
        fullpath = self.folder.joinpath(*filter(None, paths)).resolve()
        assert self.get_path(fullpath)
        if deduplicate:
            suffix = deduplicate if isinstance(deduplicate, str) else ""
            fullpath = self.deduplicate_fullpath(fullpath, suffix=suffix)
        return Path(fullpath)

    def deduplicate_fullpath(self, fullpath: Path, *, suffix: str = "") -> Path:
        if os.path.exists(fullpath):
            number = 1
            parts = os.path.splitext(fullpath)
            template = f"{parts[0]} ({suffix}%s){parts[1]}"
            while os.path.exists(fullpath):
                fullpath = Path(template % number)
                number += 1
        return fullpath
