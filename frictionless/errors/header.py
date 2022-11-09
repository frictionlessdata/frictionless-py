from __future__ import annotations
import attrs
from typing import List
from .table import TableError


@attrs.define(kw_only=True)
class HeaderError(TableError):
    """Header error representation.

    A base class for all the errors related to the resource header.
    """

    type = "header-error"
    title = "Header Error"
    description = "Cell Error"
    template = "Cell Error"
    tags = ["#table", "#header"]

    # State

    labels: List[str]
    """
    List of labels that has errors.
    """

    row_numbers: List[int]
    """
    Row number where the error occurred.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "labels": {"type": "array", "items": {"type": "string"}},
            "rowNumbers": {"type": "array", "items": {"type": "integer"}},
        },
    }


class BlankHeaderError(HeaderError):
    type = "blank-header"
    title = "Blank Header"
    description = "This header is empty. A header should contain at least one value."
    template = "Header is completely blank"
