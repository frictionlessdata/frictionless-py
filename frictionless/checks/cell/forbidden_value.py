from ... import errors
from ...check import Check


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
