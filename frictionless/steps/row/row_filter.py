from __future__ import annotations
import attrs
import simpleeval
from typing import Optional, Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_filter(Step):
    """Filter rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-filter"

    # State

    formula: Optional[Any] = None
    """
    Evaluatable expressions to filter the rows. Rows that matches the formula 
    are returned and others are ignored. The expressions are processed using 
    simpleeval library.
    """

    function: Optional[Any] = None
    """
    Python function to filter the row.
    """

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
