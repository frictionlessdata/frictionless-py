from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class InlineControl(Control):
    """Inline control representation"""

    type = "inline"

    # State

    keys: Optional[List[str]] = None
    """TODO: add docs"""

    keyed: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
