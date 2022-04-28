import simpleeval
from ...step import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


class row_filter(Step):
    """Filter rows"""

    code = "row-filter"

    def __init__(self, descriptor=None, *, formula=None, function=None):
        self.setinitial("formula", formula)
        self.setinitial("function", function)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        formula = self.get("formula")
        function = self.get("function")
        if formula:
            # NOTE: review EvalWithCompoundTypes/sync with checks
            evalclass = simpleeval.EvalWithCompoundTypes
            function = lambda row: evalclass(names=row).eval(formula)
        resource.data = table.select(function)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "formula": {type: "string"},
            "function": {},
        },
    }
