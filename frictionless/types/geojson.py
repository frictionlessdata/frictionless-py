import json
from jsonschema.validators import validator_for
from .. import config
from ..type import Type


class GeojsonType(Type):
    """Geojson type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if isinstance(cell, str):
            try:
                cell = json.loads(cell)
            except Exception:
                return None
        if not isinstance(cell, dict):
            return None
        if self.field.format in ["default", "topojson"]:
            try:
                VALIDATORS[self.field.format].validate(cell)
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        return json.dumps(cell)


# Internal


VALIDATORS = {
    "default": validator_for(config.GEOJSON_PROFILE)(config.GEOJSON_PROFILE),
    "topojson": validator_for(config.TOPOJSON_PROFILE)(config.TOPOJSON_PROFILE),
}
