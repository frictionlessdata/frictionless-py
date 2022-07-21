from __future__ import annotations
import attrs
from typing import Optional
from .metadata import Metadata
from .errors import StatsError


@attrs.define(kw_only=True)
class Stats(Metadata):

    # State

    md5: Optional[str] = None
    """TODO: add docs"""

    sha256: Optional[str] = None
    """TODO: add docs"""

    bytes: Optional[int] = None
    """TODO: add docs"""

    fields: Optional[int] = None
    """TODO: add docs"""

    rows: Optional[int] = None
    """TODO: add docs"""

    tasks: Optional[int] = None
    """TODO: add docs"""

    errors: Optional[int] = None
    """TODO: add docs"""

    seconds: Optional[float] = None
    """TODO: add docs"""

    # Metadata

    metadata_type = "stats"
    metadata_Error = StatsError
    metadata_profile = {
        "type": "object",
        "properties": {
            "md5": {"type": "string"},
            "sha256": {"type": "string"},
            "bytes": {"type": "integer"},
            "fields": {"type": "integer"},
            "rows": {"type": "integer"},
            "errors": {"type": "integer"},
            "seconds": {"type": "float"},
        },
    }
