from dataclasses import dataclass
from ...dialect import Control


@dataclass
class HtmlControl(Control):
    """Html control representation"""

    code = "html"

    # Properties

    selector: str = "table"
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "selector": {"type": "string"},
        },
    }
