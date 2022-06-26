import isodate
import datetime
from dataclasses import dataclass
from ..field2 import Field2
from .. import settings


@dataclass
class DurationField(Field2):
    type = "duration"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, (isodate.Duration, datetime.timedelta)):
                if not isinstance(cell, str):
                    return None
                try:
                    cell = isodate.parse_duration(cell)
                except Exception:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return isodate.duration_isoformat(cell)

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        13
    ]
