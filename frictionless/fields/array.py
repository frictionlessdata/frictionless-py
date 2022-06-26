import json
from typing import Optional
from dataclasses import dataclass, field
from ..field2 import Field2
from .. import settings


@dataclass
class ArrayField(Field2):
    type = "array"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    # Properties

    array_item: Optional[dict] = field(default_factory=dict)
    """TODO: add docs"""

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, list):
                if isinstance(cell, str):
                    try:
                        cell = json.loads(cell)
                    except Exception:
                        return None
                    if not isinstance(cell, list):
                        return None
                elif isinstance(cell, tuple):
                    cell = list(cell)
                else:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return json.dumps(cell)

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        12
    ]
