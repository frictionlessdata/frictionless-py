from typing import Any, Optional

import attrs
from typing_extensions import Self

from .. import helpers, settings


@attrs.define(kw_only=True, repr=False)
class Config:
    folder: Optional[str] = None
    port: int = settings.DEFAULT_HTTP_PORT
    debug: bool = False

    # Convert

    @classmethod
    def from_options(cls, *args: Any, **options: Any) -> Self:
        return cls(*args, **helpers.remove_non_values(options))
