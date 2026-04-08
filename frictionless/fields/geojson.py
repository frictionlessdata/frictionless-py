from __future__ import annotations

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class GeojsonField(Field):
    type = "geojson"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]
