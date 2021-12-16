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


class table_dimensions(Check):
    """Check for minimum and maximum table dimensions

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "table-dimensions", num_rows, min_rows, max_rows, num_fields, min_fields, max_fields}])`

    Parameters:
       descriptor (dict): check's descriptor

    """

    code = "table-dimensions"
    Errors = [errors.TableDimensionsError]

    def __init__(
        self,
        descriptor=None,
        *,
        num_rows=None,
        num_fields=None,
        min_rows=None,
        max_rows=None,
        min_fields=None,
        max_fields=None
    ):
        self.setinitial("num_rows", num_rows)
        self.setinitial("num_fields", num_fields)
        self.setinitial("min_rows", min_rows)
        self.setinitial("max_rows", max_rows)
        self.setinitial("min_fields", min_fields)
        self.setinitial("max_fields", max_fields)
        super().__init__(descriptor)
        self.__num_rows = self["num_rows"] if "num_rows" in self else -1
        self.__num_fields = self["num_fields"] if "num_fields" in self else -1
        self.__min_rows = self["min_rows"] if "min_rows" in self else -1
        self.__max_rows = self["max_rows"] if "max_rows" in self else -1
        self.__min_fields = self["min_fields"] if "min_fields" in self else -1
        self.__max_fields = self["max_fields"] if "max_fields" in self else -1

    # Validate

    def validate_start(self):
        number_fields = len(self.resource.schema.fields)

        if self.__num_fields > 0 and number_fields != self.__num_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the required number is %s"
                % (number_fields, self.__num_fields),
                limits={
                    "required_num_fields": self.__num_fields,
                    "number_fields": number_fields,
                },
            )
        if self.__min_fields > 0 and number_fields < self.__min_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the minimum is %s"
                % (number_fields, self.__min_fields),
                limits={"min_fields": self.__min_fields, "number_fields": number_fields},
            )
        if self.__max_fields > 0 and number_fields > self.__max_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the maximum is %s"
                % (number_fields, self.__max_fields),
                limits={"max_fields": self.__max_fields, "number_fields": number_fields},
            )

    def validate_row(self, row):
        self.__last_row = row
        number_rows = self.__last_row.row_number
        if self.__max_rows > 0 and self.__last_row.row_number > self.__max_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the maximum is %s"
                % (number_rows, self.__max_rows),
                limits={"max_rows": self.__max_rows, "number_rows": number_rows},
            )

    def validate_end(self):
        number_rows = self.__last_row.row_number
        if self.__num_rows > 0 and number_rows != self.__num_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the required is %s"
                % (number_rows, self.__num_rows),
                limits={"required_num_rows": self.__num_rows, "number_rows": number_rows},
            )

        if self.__min_rows > 0 and number_rows < self.__min_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the minimum is %s"
                % (number_rows, self.__min_rows),
                limits={"min_rows": self.__min_rows, "number_rows": number_rows},
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": {"oneOf": ["minRows", "maxRows", "minFields", "maxFields"]},
        "properties": {
            "min_rows": {"type": "number"},
            "max_rows": {"type": "number"},
            "min_fields": {"type": "number"},
            "max_fields": {"type": "number"},
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
