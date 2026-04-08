import json
from typing import Any, Dict, Literal, Optional, cast

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import JSONConstraints


class ObjectFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON object."""

    type: Literal["object"] = "object"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None

    def read_value(self, cell: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(cell, dict):
            if not isinstance(cell, str):
                return None
            try:
                cell = json.loads(cell)
            except Exception:
                return None
            if not isinstance(cell, dict):
                return None
        return cast(Dict[str, Any], cell)

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        return json.dumps(cell)

