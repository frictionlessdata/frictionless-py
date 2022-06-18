from typing import List, Any
from ... import errors
from ...check import Check


class forbidden_value(Check):
    """Check for forbidden values in a field"""

    code = "forbidden-value"
    Errors = [errors.ForbiddenValueError]

    def __init__(self, *, field_name: str, values: List[Any]):
        self.field_name = field_name
        self.values = values

    # Properties

    field_name: str
    """# TODO: add docs"""

    values: List[Any]
    """# TODO: add docs"""

    # Validate

    def validate_start(self):
        if self.field_name not in self.resource.schema.field_names:
            note = 'forbidden value check requires field "%s"' % self.field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row):
        cell = row[self.field_name]
        if cell in self.values:
            yield errors.ForbiddenValueError.from_row(
                row,
                note='forbiddened values are "%s"' % self.values,
                field_name=self.field_name,
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
    metadata_properties = [
        {"name": "code"},
        {"name": "fieldName"},
        {"name": "values"},
    ]
