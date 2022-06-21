from typing import Optional
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class BigqueryDialect(Dialect):
    """Bigquery dialect representation"""

    # Properties

    table: str
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
            "table": {"type": "string"},
            "dataset": {"type": "string"},
            "project": {"type": "string"},
            "prefix": {"type": "string"},
        },
    }
