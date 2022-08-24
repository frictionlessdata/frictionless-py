from __future__ import annotations
import attrs
from typing import Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class table_pivot(Step):
    """Pivot table"""

    type = "table-pivot"

    # State

    f1: str
    """NOTE: add docs
    """

    f2: str
    """NOTE: add docs
    """

    f3: str
    """NOTE: add docs
    """

    aggfun: Any
    """NOTE: add docs
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.pivot(self.f1, self.f2, self.f3, self.aggfun)  # type: ignore
        resource.infer()

    # Metadata

    metadata_profile_patch = {
        "required": ["f1", "f2", "f3", "aggfun"],
        "properties": {
            "f1": {"type": "string"},
            "f2": {"type": "string"},
            "f3": {"type": "string"},
            "aggfun": {},
        },
    }
