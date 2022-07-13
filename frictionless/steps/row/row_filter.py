from __future__ import annotations
import attrs
import simpleeval
from typing import Optional, Any
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class row_filter(Step):
    """Filter rows"""

    type = "row-filter"

    # State

    formula: Optional[Any] = None
    """TODO: add docs"""

    function: Optional[Any] = None
    """TODO: add docs"""

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

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "formula": {type: "string"},
            "function": {},
        },
    }
