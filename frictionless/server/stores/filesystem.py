from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from ..project import Project


class Filesystem:
    basepath: Path

    def __init__(self, project: Project):
        # We need to use resolve here to get an absolute path
        self.basepath = Path(project.public).resolve()

    def deduplicate_fullpath(self, fullpath: Path, *, suffix: str = "") -> Path:
        if os.path.exists(fullpath):
            number = 1
            parts = os.path.splitext(fullpath)
            template = f"{parts[0]} ({suffix}%s){parts[1]}"
            while os.path.exists(fullpath):
                fullpath = Path(template % number)
                number += 1
        return fullpath

    def get_fullpath(
        self, *paths: Optional[str], deduplicate: Optional[Union[bool, str]] = None
    ) -> Path:
        # We need to use resolve here to get normalized path
        fullpath = self.basepath.joinpath(*filter(None, paths)).resolve()
        assert self.get_path(fullpath)
        if deduplicate:
            suffix = deduplicate if isinstance(deduplicate, str) else ""
            fullpath = self.deduplicate_fullpath(fullpath, suffix=suffix)
        return Path(fullpath)

    def get_path(self, fullpath: Path) -> str:
        # We need to use resolve here to prevent path traversing
        path = str(Path(fullpath).resolve().relative_to(self.basepath))
        assert path != "."
        assert path != ""
        return path

    def get_path_and_basepath(self, path: str) -> Tuple[str, str]:
        # Round-robin to ensure that path is safe
        fullpath = self.get_fullpath(path)
        path = self.get_path(fullpath)
        return path, str(self.basepath)
