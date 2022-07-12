from typing import List
from dataclasses import dataclass
from .table import TableError


@dataclass
class HeaderError(TableError):
    """Header error representation"""

    name = "Header Error"
    type = "header-error"
    tags = ["#table", "#header"]
    template = "Cell Error"
    description = "Cell Error"

    # State

    labels: List[str]
    """TODO: add docs"""

    row_numbers: List[int]
    """TODO: add docs"""

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "name": {},
            "type": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
            "labels": {},
            "rowNumbers": {},
        },
    }


class BlankHeaderError(HeaderError):
    name = "Blank Header"
    type = "blank-header"
    template = "Header is completely blank"
    description = "This header is empty. A header should contain at least one value."
