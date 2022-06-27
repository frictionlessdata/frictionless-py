import re
from decimal import Decimal
from dataclasses import dataclass
from ...schema import Field
from ... import settings


@dataclass
class IntegerField(Field):
    type = "integer"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Properties

    bare_number: bool = settings.DEFAULT_BARE_NUMBER
    """TODO: add docs"""

    # Read

    def create_value_reader(self):

        # Create pattern
        pattern = None
        if not self.bare_number:
            pattern = re.compile(r"((^\D*)|(\D*$))")

        # Create reader
        def value_reader(cell):
            if isinstance(cell, str):
                if pattern:
                    cell = pattern.sub("", cell)
                try:
                    return int(cell)
                except Exception:
                    return None
            elif cell is True or cell is False:
                return None
            elif isinstance(cell, int):
                return cell
            elif isinstance(cell, float) and cell.is_integer():
                return int(cell)
            elif isinstance(cell, Decimal) and cell % 1 == 0:
                return int(cell)
            return None

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return str(cell)

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        2
    ].copy()
    metadata_profile["properties"]["missingValues"] = {}
