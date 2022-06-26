from dateutil import parser
from datetime import datetime
from dataclasses import dataclass
from ..field2 import Field2
from .. import settings


@dataclass
class DatetimeField(Field2):
    type = "datetime"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, datetime):
                if not isinstance(cell, str):
                    return None
                try:
                    if self.format == "default":
                        # Guard against shorter formats supported by dateutil
                        assert cell[16] == ":"
                        assert len(cell) >= 19
                        cell = parser.isoparse(cell)
                    elif self.format == "any":
                        cell = parser.parse(cell)
                    else:
                        cell = datetime.strptime(cell, self.format)
                except Exception:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create format
        format = self.format
        if format == settings.DEFAULT_FIELD_FORMAT:
            format = settings.DEFAULT_DATETIME_PATTERN

        # Create writer
        def value_writer(cell):
            cell = cell.strftime(format)
            cell = cell.replace("+0000", "Z")
            return cell

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        3
    ]
