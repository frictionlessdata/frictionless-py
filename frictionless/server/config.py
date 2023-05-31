import attrs
from typing import Optional, Any
from typing_extensions import Self
from .. import settings
from .. import helpers


@attrs.define(kw_only=True, repr=False)
class Config:
    folder: Optional[str] = None
    port: int = settings.DEFAULT_HTTP_PORT
    debug: bool = False

    # Convert

    @classmethod
    def from_options(cls, *args: Any, **options: Any) -> Self:
        return cls(*args, **helpers.remove_non_values(options))
