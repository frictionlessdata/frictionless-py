from __future__ import annotations

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class ObjectField(Field):
    type = "object"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]
