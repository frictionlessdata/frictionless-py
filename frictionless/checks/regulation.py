import simpleeval
from .. import errors
from ..check import Check


class forbidden_value(Check):
    """Check for forbidden values in a field

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "backlisted-value", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       field_name (str): a field name to look into
       forbidden (any[]): a list of forbidden values

    """

    code = "forbidden-value"
    Errors = [errors.ForbiddenValueError]

    def __init__(self, descriptor=None, *, field_name=None, values=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("values", values)
        super().__init__(descriptor)
        self.__field_name = self["fieldName"]
        self.__values = self["values"]

    # Validate

    def validate_start(self):
        if self.__field_name not in self.resource.schema.field_names:
            note = 'forbidden value check requires field "%s"' % self.__field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row):
        cell = row[self.__field_name]
        if cell in self.__values:
            yield errors.ForbiddenValueError.from_row(
                row,
                note='forbiddened values are "%s"' % self.__values,
                field_name=self.__field_name,
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["fieldName", "values"],
        "properties": {
            "fieldName": {"type": "string"},
            "values": {"type": "array"},
        },
    }


class sequential_value(Check):
    """Check that a column having sequential values

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "sequential-value", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       field_name (str): a field name to check

    """

    code = "sequential-value"
    Errors = [errors.SequentialValueError]

    def __init__(self, descriptor=None, *, field_name=None):
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)
        self.__field_name = self.get("fieldName")
        self.__cursor = None
        self.__exited = False

    # Validate

    def validate_start(self):
        if self.__field_name not in self.resource.schema.field_names:
            note = 'sequential value check requires field "%s"' % self.__field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row):
        if not self.__exited:
            cell = row[self.__field_name]
            try:
                self.__cursor = self.__cursor or cell
                assert self.__cursor == cell
                self.__cursor += 1
            except Exception:
                self.__exited = True
                yield errors.SequentialValueError.from_row(
                    row,
                    note="the value is not sequential",
                    field_name=self.__field_name,
                )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["fieldName"],
        "properties": {"fieldName": {"type": "string"}},
    }


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
