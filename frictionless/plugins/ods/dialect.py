from typing import Union
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class OdsDialect(Dialect):
    """Ods dialect representation"""

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
