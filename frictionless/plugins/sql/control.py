from typing import Optional
from dataclasses import dataclass
from ...control import Control


@dataclass
class SqlControl(Control):
    """SQL control representation"""

    code = "sql"

    # Properties

    table: str
    """TODO: add docs"""

    prefix: str = ""
    """TODO: add docs"""

    order_by: Optional[str] = None
    """TODO: add docs"""

    where: Optional[str] = None
    """TODO: add docs"""

    namespace: Optional[str] = None
    """TODO: add docs"""

    basepath: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["table"],
        "additionalProperties": False,
        "properties": {
            "table": {"type": "string"},
            "prefix": {"type": "string"},
            "order_by": {"type": "string"},
            "where": {"type": "string"},
            "namespace": {"type": "string"},
            "basepath": {"type": "string"},
        },
    }
