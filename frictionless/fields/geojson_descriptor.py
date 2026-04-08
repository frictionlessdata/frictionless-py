import json
from typing import Any, Dict, Literal, Optional, cast

from .. import settings
from ..platform import platform
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import BaseConstraints


class GeoJSONFieldDescriptor(BaseFieldDescriptor):
    """The field contains a JSON object according to GeoJSON or TopoJSON spec."""

    type: Literal["geojson"] = "geojson"
    format: Optional[Literal["default", "topojson"]] = None
    constraints: Optional[BaseConstraints[str]] = None

    def read_value(self, cell: Any) -> Optional[Dict[str, Any]]:
        validator_for = platform.jsonschema_validators.validator_for  # type: ignore
        validators = {  # type: ignore
            "default": validator_for(settings.GEOJSON_PROFILE)(settings.GEOJSON_PROFILE),
            "topojson": validator_for(settings.TOPOJSON_PROFILE)(
                settings.TOPOJSON_PROFILE
            ),
        }

        if isinstance(cell, str):
            try:
                cell = json.loads(cell)
            except Exception:
                return None
        if not isinstance(cell, dict):
            return None
        if self.format in ["default", "topojson"]:
            try:
                validators[self.format].validate(cell)  # type: ignore
            except Exception:
                return None
        return cast(Dict[str, Any], cell)

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        return json.dumps(cell)

