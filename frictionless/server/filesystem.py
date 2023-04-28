from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Union
from ..resource import Resource


class Filesystem:
    folder: Path

    def __init__(self, folder: str):
        # We need to use resolve here to get an absolute path
        self.folder = Path(folder).resolve()

    def deduplicate_fullpath(self, fullpath: str, *, suffix: str = "") -> str:
        if os.path.exists(fullpath):
            number = 1
            parts = os.path.splitext(fullpath)
            template = f"{parts[0]} ({suffix}%s){parts[1]}"
            while os.path.exists(fullpath):
                fullpath = template % number
                number += 1
        return fullpath

    def get_fullpath(
        self, *paths: Optional[str], deduplicate: Optional[Union[bool, str]] = None
    ) -> str:
        # We need to use resolve here to get normalized path
        fullpath = str(self.folder.joinpath(*filter(None, paths)).resolve())
        assert self.get_relpath(fullpath)
        if deduplicate:
            suffix = deduplicate if isinstance(deduplicate, str) else ""
            fullpath = self.deduplicate_fullpath(fullpath, suffix=suffix)
        return fullpath

    def get_relpath(self, fullpath: str) -> str:
        # We need to use resolve here to prevent path traversing
        path = str(Path(fullpath).resolve().relative_to(self.folder))
        assert path != "."
        assert path != ""
        return path

    def get_filetype(self, path: str) -> Optional[str]:
        resource = Resource(path=path)
        return resource.datatype

    def get_filename(self, path: str) -> str:
        return os.path.basename(path)

    def get_folder(self, path: str) -> str:
        return os.path.dirname(path)

    def is_hidden_path(self, path: str) -> bool:
        for part in os.path.split(path):
            if part.startswith(".") and len(part) > 1:
                return True
        return False

    def is_basepath(self, path: str) -> bool:
        return self.folder.samefile(path)

    def is_existent(self, fullpath: str) -> bool:
        return os.path.exists(fullpath)

    def is_filename(self, name: str) -> bool:
        return not os.path.dirname(name)

    def is_folder(self, fullpath: str) -> bool:
        return os.path.isdir(fullpath)

    def is_file(self, fullpath: str) -> bool:
        return os.path.isfile(fullpath)
