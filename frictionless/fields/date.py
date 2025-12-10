from __future__ import annotations

import attrs
from ..schema import Field

@attrs.define(kw_only=True, repr=False)
class DateField(Field):
    type = "date"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

