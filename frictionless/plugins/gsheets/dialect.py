from typing import Optional
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class GsheetsDialect(Dialect):
    """Gsheets dialect representation"""

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
