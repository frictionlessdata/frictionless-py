from __future__ import annotations
import attrs
from ..schema import Field
from .. import settings


@attrs.define(kw_only=True)
class AnyField(Field):
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

        # Create writer
        def value_writer(cell):
            return str(cell)

        return value_writer

    # Metadata

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        14
    ].copy()
    metadata_profile["properties"]["missingValues"] = {}
