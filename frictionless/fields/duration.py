from __future__ import annotations

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class DurationField(Field):
    type = "duration"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]
