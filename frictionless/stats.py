from __future__ import annotations
import attrs
from typing import Optional
from .metadata import Metadata
from .errors import StatsError


@attrs.define(kw_only=True)
class Stats(Metadata):
    """Stats representation

    This class stores stats of the validation task.

    """

    # State

    md5: Optional[str] = None
    """
    Hashed value of data with md5 hashing algorithm.
    """

    sha256: Optional[str] = None
    """
    Hashed value of data with sha256 hashing algorithm.
    """

    bytes: Optional[int] = None
    """
    Size of data in bytes.
    """

    fields: Optional[int] = None
    """
    Number of fields in a resource.
    """

    rows: Optional[int] = None
    """
    Number of rows in a resource.
    """

    tasks: Optional[int] = None
    """
    Number of resource to validate.
    """

    warnings: Optional[int] = None
    """
    Number of warnings from the validation task. Warnings are information to 
    users about non severe problems such as "limits reached".
    """

    errors: Optional[int] = None
    """
    Number of errors from the validation task.
    """

    seconds: Optional[float] = None
    """
    Time taken in secs to validate a resource.
    """

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
            "tasks": {"type": "integer"},
            "warnings": {"type": "integer"},
            "errors": {"type": "integer"},
            "seconds": {"type": "number"},
        },
    }
