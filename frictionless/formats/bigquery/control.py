import attrs
from typing import Optional
from ...dialect import Control


@attrs.define
class BigqueryControl(Control):
    """Bigquery control representation"""

    type = "bigquery"

    # State

    table: Optional[str] = None
    """TODO: add docs"""

    dataset: Optional[str] = None
    """TODO: add docs"""

    project: Optional[str] = None
    """TODO: add docs"""

    prefix: Optional[str] = ""
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["table"],
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "table": {"type": "string"},
            "dataset": {"type": "string"},
            "project": {"type": "string"},
            "prefix": {"type": "string"},
        },
    }
