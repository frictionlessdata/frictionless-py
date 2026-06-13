from __future__ import annotations

from typing import Any, Dict

from ...schema import Field, Schema
from ...system import Mapper


class JsonschemaMapper(Mapper):
    """ERD Mapper"""

    # Write

    def read_schema(self, profile: Dict[str, Any]) -> Schema:  # type: ignore
        schema = Schema()
        required = profile.get("required", [])
        assert isinstance(required, list)
        properties = profile.get("properties", {})
        assert isinstance(properties, dict)
        for name, prop in properties.items():
            # Type
            type = prop.get("type", "any")
            assert isinstance(type, str)
            if type not in ["string", "integer", "number", "boolean", "object", "array"]:
                type = "any"

            # Field
            assert isinstance(name, str)
            assert isinstance(prop, dict)
            field_descriptor = {"type": type, "name": name}
            
            # Description
            description = prop.get("description")  # type: ignore
            if description:
                assert isinstance(description, str)
                field_descriptor["description"] = description
            
            field = Field.from_descriptor(field_descriptor)
            schema.add_field(field)

            # Required
            if name in required:
                field.required = True

        return schema
