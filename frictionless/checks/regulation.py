import simpleeval
from .. import errors
from ..check import Check


class forbidden_value(Check):
    """Check for forbidden values in a field

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(extra_checks=[('backlisted-value', {...})])`

    This check can be enabled using the `extra_checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       field_name (str): a field name to look into
       forbidden (any[]): a list of forbidden values

    """

    code = "forbidden-value"
    Errors = [errors.ForbiddenValueError]

    def __init__(self, descriptor=None, *, field_name=None, forbidden=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("forbidden", forbidden)
        super().__init__(descriptor)

    def prepare(self):
        self.__field_name = self["fieldName"]
        self.__forbidden = self["forbidden"]

    # Validate

    def validate_task(self):
        if self.__field_name not in self.table.schema.field_names:
            note = 'forbidden value check requires field "%s"' % self.__field_name
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell = row[self.__field_name]
        if cell in self.__forbidden:
            yield errors.ForbiddenValueError.from_row(
                row,
                note='forbiddened values are "%s"' % self.__forbidden,
                field_name=self.__field_name,
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["fieldName", "forbidden"],
        "properties": {
            "fieldName": {"type": "string"},
            "forbidden": {"type": "array"},
        },
    }


class sequential_value(Check):
    """Check that a column having sequential values

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(extra_checks=[('sequential-value', {...})])`

    This check can be enabled using the `extra_checks` parameter
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

    def prepare(self):
        self.__cursor = None
        self.__exited = False
        self.__field_name = self.get("fieldName")

    # Validate

    def validate_task(self):
        if self.__field_name not in self.table.schema.field_names:
            note = 'sequential value check requires field "%s"' % self.__field_name
            yield errors.TaskError(note=note)

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
    Implicit | `validate(extra_checks=(['row-constraint', {...})])`

    This check can be enabled using the `extra_checks` parameter
    for the `validate` function. The syntax for the row constraint
    check can be found here - https://github.com/danthedeckie/simpleeval

    Parameters:
       descriptor (dict): check's descriptor
       constraint (str): a python expression to evaluate against a row

    """

    code = "row-constraint"
    Errors = [errors.RowConstraintError]

    def __init__(self, descriptor=None, *, constraint=None):
        self.setinitial("constraint", constraint)
        super().__init__(descriptor)

    def prepare(self):
        self.__constraint = self["constraint"]

    # Validate

    def validate_row(self, row):
        try:
            # This call should be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            assert simpleeval.simple_eval(self.__constraint, names=row)
        except Exception:
            yield errors.RowConstraintError.from_row(
                row,
                note='the row constraint to conform is "%s"' % self.__constraint,
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["constraint"],
        "properties": {"constraint": {"type": "string"}},
    }
