from __future__ import annotations

import json
from typing import Any, Dict, cast

import attrs

from .. import settings
from ..platform import platform
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class GeojsonField(Field):
    type = "geojson"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    # TODO: use different value_readers based on format (see string)
    def create_value_reader(self):
        validator_for = platform.jsonschema_validators.validator_for  # type: ignore
        validators = {  # type: ignore
            "default": validator_for(settings.GEOJSON_PROFILE)(settings.GEOJSON_PROFILE),
            "topojson": validator_for(settings.TOPOJSON_PROFILE)(
                settings.TOPOJSON_PROFILE
            ),
        }

        # Create reader
        def value_reader(cell: Any):
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

        return value_reader

    # Write

    def create_value_writer(self):
        # Create writer
        def value_writer(cell: Any):
            return json.dumps(cell)

        return value_writer

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "format": {
                "type": "string",
                "enum": ["default", "topojson"],
            },
        }
    }
