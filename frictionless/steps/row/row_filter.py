import simpleeval
from typing import Optional, Any
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_filter(Step):
    """Filter rows"""

    code = "row-filter"

    def __init__(
        self,
        *,
        formula: Optional[Any] = None,
        function: Optional[Any] = None,
    ):
        self.formula = formula
        self.function = function

    # Properties

    formula: Optional[Any]
    """TODO: add docs"""

    function: Optional[Any]
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
            "code": {},
            "formula": {type: "string"},
            "function": {},
        },
    }
