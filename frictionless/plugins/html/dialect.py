from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class HtmlDialect(Dialect):
    """Html dialect representation"""

    # Properties

    credentials: str = "table"
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "selector": {"type": "string"},
        },
    }
