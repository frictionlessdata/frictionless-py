from typing import Union
from dataclasses import dataclass
from ...dialect import Control
from . import settings


@dataclass
class OdsControl(Control):
    """Ods control representation"""

    type = "ods"

    # State

    sheet: Union[str, int] = settings.DEFAULT_SHEET
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {},
            "sheet": {"type": ["number", "string"]},
        },
    }
