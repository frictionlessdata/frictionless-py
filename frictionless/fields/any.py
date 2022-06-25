from dataclasses import dataclass
from ..field2 import Field2
from .. import settings


@dataclass
class AnyField(Field2):
    type = "any"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create reader
        def value_writer(cell):
            return str(cell)

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        14
    ]
