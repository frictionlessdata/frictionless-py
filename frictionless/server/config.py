import attrs
from typing import Optional
from typing_extensions import Self
from .. import settings
from .. import helpers


@attrs.define(kw_only=True)
class Config:
    folder: Optional[str] = None
    port: int = settings.DEFAULT_SERVER_PORT
    debug: bool = False

    # Convert

    @classmethod
    def from_options(cls, *args, **options) -> Self:
        return cls(*args, **helpers.remove_non_values(options))
