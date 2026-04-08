from __future__ import annotations

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class StringField(Field):
    type = "string"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "pattern",
        "enum",
    ]
