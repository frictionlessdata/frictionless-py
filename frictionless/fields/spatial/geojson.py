from __future__ import annotations
import json
import attrs
from jsonschema.validators import validator_for
from ...schema import Field
from ... import settings


@attrs.define(kw_only=True)
class GeojsonField(Field):
    type = "geojson"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if isinstance(cell, str):
                try:
                    cell = json.loads(cell)
                except Exception:
                    return None
            if not isinstance(cell, dict):
                return None
            if self.format in ["default", "topojson"]:
                try:
                    validators[self.format].validate(cell)
                except Exception:
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
        11
    ].copy()
    metadata_profile["properties"]["missingValues"] = {}
    metadata_profile["properties"]["example"] = {}


# Internal


validators = {
    "default": validator_for(settings.GEOJSON_PROFILE)(settings.GEOJSON_PROFILE),
    "topojson": validator_for(settings.TOPOJSON_PROFILE)(settings.TOPOJSON_PROFILE),
}
