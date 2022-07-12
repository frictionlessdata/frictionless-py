from typing import Optional
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class GsheetsControl(Control):
    """Gsheets control representation"""

    type = "gsheets"

    # State

    credentials: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "credentials": {"type": "string"},
        },
    }
