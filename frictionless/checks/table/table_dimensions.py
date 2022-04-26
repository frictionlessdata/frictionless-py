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
        descriptor=None,
        *,
        num_rows=None,
        num_fields=None,
        min_rows=None,
        max_rows=None,
        min_fields=None,
        max_fields=None
    ):
        self.setinitial("numRows", num_rows)
        self.setinitial("numFields", num_fields)
        self.setinitial("minRows", min_rows)
        self.setinitial("maxRows", max_rows)
        self.setinitial("minFields", min_fields)
        self.setinitial("maxFields", max_fields)
        super().__init__(descriptor)
        self.__num_rows = self["numRows"] if "numRows" in self else -1
        self.__num_fields = self["numFields"] if "numFields" in self else -1
        self.__min_rows = self["minRows"] if "minRows" in self else -1
        self.__max_rows = self["maxRows"] if "maxRows" in self else -1
        self.__min_fields = self["minFields"] if "minFields" in self else -1
        self.__max_fields = self["maxFields"] if "maxFields" in self else -1

    # Validate

    def validate_start(self):
        number_fields = len(self.resource.schema.fields)

        # Check if there is a different number of fields as required
        if self.__num_fields > 0 and number_fields != self.__num_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the required number is %s"
                % (number_fields, self.__num_fields),
                limits={
                    "requiredNumFields": self.__num_fields,
                    "numberFields": number_fields,
                },
            )

        # Check if there is less field than the minimum
        if self.__min_fields > 0 and number_fields < self.__min_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the minimum is %s"
                % (number_fields, self.__min_fields),
                limits={"minFields": self.__min_fields, "numberFields": number_fields},
            )

        # Check if there is more field than the maximum
        if self.__max_fields > 0 and number_fields > self.__max_fields:
            yield errors.TableDimensionsError(
                note="Current number of fields is %s, the maximum is %s"
                % (number_fields, self.__max_fields),
                limits={"maxFields": self.__max_fields, "numberFields": number_fields},
            )

    def validate_row(self, row):
        self.__last_row = row
        number_rows = self.__last_row.row_number
        # Check if exceed the max number of rows
        if self.__max_rows > 0 and self.__last_row.row_number > self.__max_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the maximum is %s"
                % (number_rows, self.__max_rows),
                limits={"maxRows": self.__max_rows, "numberRows": number_rows},
            )

    def validate_end(self):
        number_rows = self.__last_row.row_number

        # Check if doesn't have the exact number of rows
        if self.__num_rows > 0 and number_rows != self.__num_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the required is %s"
                % (number_rows, self.__num_rows),
                limits={"requiredNumRows": self.__num_rows, "numberRows": number_rows},
            )

        # Check if has less rows than the required
        if self.__min_rows > 0 and number_rows < self.__min_rows:
            yield errors.TableDimensionsError(
                note="Current number of rows is %s, the minimum is %s"
                % (number_rows, self.__min_rows),
                limits={"minRows": self.__min_rows, "numberRows": number_rows},
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
            "numRows": {"type": "number"},
            "minRows": {"type": "number"},
            "maxRows": {"type": "number"},
            "numFields": {"type": "number"},
            "minFields": {"type": "number"},
            "maxFields": {"type": "number"},
        },
    }
