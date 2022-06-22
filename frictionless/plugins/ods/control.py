from typing import Union
from dataclasses import dataclass
from ...control import Control


@dataclass
class OdsControl(Control):
    """Ods control representation"""

    code = "ods"

    # Properties

    sheet: Union[str, int] = 1
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sheet": {"type": ["number", "string"]},
        },
    }
