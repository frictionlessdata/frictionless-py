from typing import List
from dataclasses import dataclass
from .table import TableError


@dataclass
class HeaderError(TableError):
    """Header error representation"""

    code = "header-error"
    name = "Header Error"
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
            "code": {},
            "name": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
            "labels": {},
            "rowNumbers": {},
        },
    }


class BlankHeaderError(HeaderError):
    code = "blank-header"
    name = "Blank Header"
    template = "Header is completely blank"
    description = "This header is empty. A header should contain at least one value."
