from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class InlineControl(Control):
    """Inline control representation"""

    code = "inline"

    # Properties

    keys: Optional[List[str]] = None
    """TODO: add docs"""

    keyed: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
