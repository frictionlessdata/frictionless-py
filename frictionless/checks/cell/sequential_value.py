from ... import errors
from ...check import Check


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
