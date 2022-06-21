from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class JsonDialect(Dialect):
    """Json dialect representation"""

    keys: Optional[List[str]] = None
    """TODO: add docs"""

    keyed: bool = False
    """TODO: add docs"""

    property: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
        },
    }
