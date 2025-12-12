from __future__ import annotations

import attrs
from typing import Any, Dict, Optional

from ..fields.number_descriptor import NumberFieldDescriptor
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class NumberField(Field):
    type = "number"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]
    decimal_char: Optional[str] = None
    group_char: Optional[str] = None
    bare_number: Optional[bool] = None

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # Initialize _descriptor from Field properties if not already set
        if self._descriptor is None:
            descriptor_dict: Dict[str, Any] = {
                "name": self.name,
                "type": self.type,
            }
            if self.format:
                descriptor_dict["format"] = self.format
            if self.decimal_char is not None:
                descriptor_dict["decimalChar"] = self.decimal_char
            if self.group_char is not None:
                descriptor_dict["groupChar"] = self.group_char
            if self.bare_number is not None:
                descriptor_dict["bareNumber"] = self.bare_number
            if self.title is not None:
                descriptor_dict["title"] = self.title
            if self.description is not None:
                descriptor_dict["description"] = self.description
            if self.missing_values:
                descriptor_dict["missingValues"] = self.missing_values
            if self.constraints:
                descriptor_dict["constraints"] = self.constraints
            if self.example is not None:
                descriptor_dict["example"] = self.example
            
            try:
                self._descriptor = NumberFieldDescriptor.model_validate(descriptor_dict)
            except Exception:
                # If validation fails, leave _descriptor as None
                pass
