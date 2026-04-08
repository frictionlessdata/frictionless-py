from __future__ import annotations

import json
from typing import Any, Literal, Optional

from pydantic import Field as PydanticField

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import JSONConstraints


class ArrayFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON array."""

    type: Literal["array"] = "array"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None
    # TODO: check later:
    # arrayItem in Frictionless schemas is an unnamed field-like descriptor to prevent using a full FieldDescriptor with "name" (backward compatibility)
    array_item: Optional[dict[str, Any]] = PydanticField(default=None, alias="arrayItem")

    def read_value(self, cell: Any) -> Optional[list[Any]]:
        if not isinstance(cell, list):
            if isinstance(cell, str):
                try:
                    cell = json.loads(cell)
                except Exception:
                    return None
                if not isinstance(cell, list):
                    return None
            elif isinstance(cell, tuple):
                cell = list(cell)  # type: ignore[arg-type]
            else:
                return None
        return cell  # type: ignore[return-value]

    def write_value(self, cell: Any) -> str:
        return json.dumps(cell)


