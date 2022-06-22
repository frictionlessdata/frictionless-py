from typing import Optional
from dataclasses import dataclass
from ...control import Control


@dataclass
class GsheetsControl(Control):
    """Gsheets control representation"""

    code = "gsheets"

    # Properties

    credentials: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "credentials": {"type": "string"},
        },
    }
