import json
import jsonschema
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
        if self.field.format == "default":
            try:
                validator.validate(cell)
            except Exception:
                return None
        elif self.field.format == "topojson":
            pass  # Accept any dict as possibly topojson for now
        return cell

    # Write

    def write_cell(self, cell):
        return json.dumps(cell)


# Internal


validator = jsonschema.validators.validator_for(config.GEOJSON_PROFILE)(
    config.GEOJSON_PROFILE
)
