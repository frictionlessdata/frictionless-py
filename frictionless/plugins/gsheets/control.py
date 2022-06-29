from typing import Optional
from dataclasses import dataclass
from ...dialect import Control


@dataclass
class GsheetsControl(Control):
    """Gsheets control representation"""

    code = "gsheets"

    # State

    credentials: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "code": {},
            "credentials": {"type": "string"},
        },
    }
