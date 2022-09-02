from __future__ import annotations
import attrs
import simpleeval
from typing import Optional, Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_filter(Step):
    """Filter rows"""

    type = "row-filter"

    # State

    formula: Optional[Any] = None
    """NOTE: add docs"""

    function: Optional[Any] = None
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        function = self.function
        table = resource.to_petl()
        if self.formula:
            # NOTE: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes
            function = lambda row: evalclass(names=row).eval(self.formula)
        resource.data = table.select(function)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "formula": {"type": "string"},
            "function": {},
        },
    }
