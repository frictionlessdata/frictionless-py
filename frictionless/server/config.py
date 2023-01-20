import attrs
from typing import Optional
from typing_extensions import Self
from .. import settings
from .. import helpers


DEFAULT_BASEPATH = ".server"


@attrs.define(kw_only=True)
class Config:
    basepath: Optional[str] = None
    is_root: bool = False
    port: int = settings.DEFAULT_SERVER_PORT
    debug: bool = False

    def __attrs_post_init__(self):
        if not self.basepath and not self.is_root:
            self.basepath = DEFAULT_BASEPATH

    # Convert

    @classmethod
    def from_options(cls, *args, **options) -> Self:
        return cls(*args, **helpers.remove_non_values(options))
