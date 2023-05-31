from __future__ import annotations
import attrs
from typing import Optional


@attrs.define(kw_only=True, repr=False)
class ResourceStats:
    """Stats representation"""

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
