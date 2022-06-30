from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class InlineControl(Control):
    """Inline control representation"""

    code = "inline"

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
            "code": {},
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
