from __future__ import annotations
import re
import attrs
from decimal import Decimal
from ..schema import Field
from .. import settings


@attrs.define(kw_only=True)
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
    """NOTE: add docs"""

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

    metadata_profile_patch = {
        "properties": {
            "bareNumber": {"type": "boolean"},
        }
    }
