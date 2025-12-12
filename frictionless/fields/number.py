from __future__ import annotations

import attrs
from typing import Optional

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
    float_number: Optional[bool] = None


