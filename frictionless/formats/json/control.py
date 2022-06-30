from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class JsonControl(Control):
    """Json control representation"""

    code = "json"

    # State

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
            "code": {},
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
        },
    }
