from typing import Optional, List
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class InlineDialect(Dialect):
    """Inline dialect representation"""

    # Properties

    keys: Optional[List[str]] = None
    """TODO: add docs"""

    keyed: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
