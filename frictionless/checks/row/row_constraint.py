import simpleeval
from ... import errors
from ...check import Check


class row_constraint(Check):
    """Check that every row satisfies a provided Python expression

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "row-constraint", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function. The syntax for the row constraint
    check can be found here - https://github.com/danthedeckie/simpleeval

    Parameters:
       descriptor (dict): check's descriptor
       formula (str): a python expression to evaluate against a row

    """

    code = "row-constraint"
    Errors = [errors.RowConstraintError]

    def __init__(self, descriptor=None, *, formula=None):
        self.setinitial("formula", formula)
        super().__init__(descriptor)
        self.__formula = self["formula"]

    # Validate

    def validate_row(self, row):
        try:
            # This call should be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            # NOTE: review EvalWithCompoundTypes/sync with steps
            evalclass = simpleeval.EvalWithCompoundTypes
            assert evalclass(names=row).eval(self.__formula)
        except Exception:
            yield errors.RowConstraintError.from_row(
                row,
                note='the row constraint to conform is "%s"' % self.__formula,
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["formula"],
        "properties": {"formula": {"type": "string"}},
    }
