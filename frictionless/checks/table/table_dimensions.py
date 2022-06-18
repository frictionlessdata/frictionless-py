from typing import Optional
from ... import errors
from ...check import Check


class table_dimensions(Check):
    """Check for minimum and maximum table dimensions

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "table-dimensions", numRows, minRows, maxRows, numFields, minFields, maxFields}])`

    Parameters:
       descriptor (dict): check's descriptor

    """

    code = "table-dimensions"
    Errors = [errors.TableDimensionsError]

    def __init__(
        self,
        *,
        num_rows: Optional[int] = None,
        min_rows: Optional[int] = None,
        max_rows: Optional[int] = None,
        num_fields: Optional[int] = None,
        min_fields: Optional[int] = None,
        max_fields: Optional[int] = None
    ):
        self.num_rows = num_rows
        self.min_rows = min_rows
        self.max_rows = max_rows
        self.num_fields = num_fields
        self.min_fields = min_fields
        self.max_fields = max_fields

    # Properties

    num_rows: Optional[int]
    """# TODO: add docs"""

    min_rows: Optional[int]
    """# TODO: add docs"""

    max_rows: Optional[int]
    """# TODO: add docs"""

    num_fields: Optional[int]
    """# TODO: add docs"""

    min_fields: Optional[int]
    """# TODO: add docs"""

    max_fields: Optional[int]
    """# TODO: add docs"""

    # Validate

    def validate_start(self):
        number_fields = len(self.resource.schema.fields)

        # Check if there is a different number of fields as required
        if self.num_fields and number_fields != self.num_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the required number is %s"
                % (number_fields, self.num_fields),
                limits={
                    "requiredNumFields": self.num_fields,
                    "numberFields": number_fields,
                },
            )

        # Check if there is less field than the minimum
        if self.min_fields and number_fields < self.min_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the minimum is %s"
                % (number_fields, self.min_fields),
                limits={"minFields": self.min_fields, "numberFields": number_fields},
            )

        # Check if there is more field than the maximum
        if self.max_fields and number_fields > self.max_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the maximum is %s"
                % (number_fields, self.max_fields),
                limits={"maxFields": self.max_fields, "numberFields": number_fields},
            )

    def validate_row(self, row):
        self.last_row = row
        number_rows = self.last_row.row_number
        # Check if exceed the max number of rows
        if self.max_rows and self.last_row.row_number > self.max_rows:  # type: ignore
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the maximum is %s"
                % (number_rows, self.max_rows),
                limits={"maxRows": self.max_rows, "numberRows": number_rows},
            )

    def validate_end(self):
        number_rows = self.last_row.row_number

        # Check if doesn't have the exact number of rows
        if self.num_rows and number_rows != self.num_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the required is %s"
                % (number_rows, self.num_rows),
                limits={"requiredNumRows": self.num_rows, "numberRows": number_rows},
            )

        # Check if has less rows than the required
        if self.min_rows and number_rows < self.min_rows:  # type: ignore
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the minimum is %s"
                % (number_rows, self.min_rows),
                limits={"minRows": self.min_rows, "numberRows": number_rows},
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": {
            "oneOf": [
                "numRows",
                "minRows",
                "maxRows",
                "numFields",
                "minFields",
                "maxFields",
            ]
        },
        "properties": {
            "code": {},
            "numRows": {"type": "number"},
            "minRows": {"type": "number"},
            "maxRows": {"type": "number"},
            "numFields": {"type": "number"},
            "minFields": {"type": "number"},
            "maxFields": {"type": "number"},
        },
    }
