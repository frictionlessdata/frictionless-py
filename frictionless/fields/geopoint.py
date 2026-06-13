from __future__ import annotations

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class GeopointField(Field):
    type = "geopoint"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]
