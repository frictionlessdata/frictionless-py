from __future__ import annotations
import attrs
import statistics
from ...checklist import Check
from ... import errors


DEFAULT_INTERVAL = 3
DEFAULT_AVERAGE = "mean"
AVERAGE_FUNCTIONS = {
    "mean": statistics.mean,
    "median": statistics.median,
    "mode": statistics.mode,
}


@attrs.define(kw_only=True)
class deviated_value(Check):
    """Check for deviated values in a field."""

    type = "deviated-value"
    Errors = [errors.DeviatedValueError]

    # State

    field_name: str
    """
    Name of the field to which the check will be applied.
    Check will not be applied to fields other than this.
    """

    interval: int = DEFAULT_INTERVAL
    """
    Interval specifies number of standard deviation away from the mean. 
    The default value is 3.
    """

    average: str = DEFAULT_AVERAGE
    """
    It specifies preferred method to calculate average of the data.
    Default value is "mean". Supported average calculation methods
    are "mean", "median", and "mode".
    """

    # Connect

    def connect(self, resource):
        super().connect(resource)
        self.__cells = []
        self.__row_numbers = []
        self.__average_function = AVERAGE_FUNCTIONS.get(self.average)

    # Validate

    def validate_start(self):
        numeric = ["integer", "number"]
        if self.field_name not in self.resource.schema.field_names:  # type: ignore
            note = 'deviated value check requires field "%s" to exist'
            yield errors.CheckError(note=note % self.field_name)
        elif self.resource.schema.get_field(self.field_name).type not in numeric:  # type: ignore
            note = 'deviated value check requires field "%s" to be numeric'
            yield errors.CheckError(note=note % self.field_name)
        if not self.__average_function:
            note = 'deviated value check supports only average functions "%s"'
            note = note % ", ".join(AVERAGE_FUNCTIONS.keys())
            yield errors.CheckError(note=note)

    def validate_row(self, row):
        cell = row[self.field_name]
        if cell is not None:
            self.__cells.append(cell)
            self.__row_numbers.append(row.row_number)
        yield from []

    def validate_end(self):
        if len(self.__cells) < 2:
            return

        # Prepare interval
        try:
            stdev = statistics.stdev(self.__cells)
            average = self.__average_function(self.__cells)  # type: ignore
            minimum = average - stdev * self.interval
            maximum = average + stdev * self.interval
        except Exception as exception:
            note = 'calculation issue "%s"' % exception
            yield errors.DeviatedValueError(note=note)
            return

        # Check values
        for row_number, cell in zip(self.__row_numbers, self.__cells):
            if not (minimum <= cell <= maximum):
                note = 'value "%s" in row at position "%s" and field "%s" is deviated "[%.2f, %.2f]"'
                note = note % (cell, row_number, self.field_name, minimum, maximum)
                yield errors.DeviatedValueError(note=note)

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "interval": {"type": "number"},
            "average": {"type": "string"},
        },
    }
