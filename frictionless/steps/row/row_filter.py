from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import attrs
import simpleeval  # type: ignore

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class row_filter(Step):
    """Filter rows.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "row-filter"

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

    def transform_resource(self, resource: Resource):
        function = self.function
        table = resource.to_petl()  # type: ignore
        if self.formula:
            # NOTE: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes  # type: ignore
            function = lambda row: evalclass(names=row).eval(self.formula)  # type: ignore
        resource.data = table.select(function)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "formula": {"type": "string"},
            "function": {},
        },
    }
