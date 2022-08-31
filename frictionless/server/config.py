from typing import Optional
from typing_extensions import Self
from .. import helpers


DEFAULT_BASEPATH = ".server"


class Config:
    basepath: Optional[str]
    root: bool

    def __init__(self, *, basepath: Optional[str] = None, root: bool = False):
        self.basepath = basepath or (None if root else DEFAULT_BASEPATH)
        self.root = root

    # Convert

    @classmethod
    def from_options(cls, *args, **options) -> Self:
        return cls(*args, **helpers.remove_non_values(options))
