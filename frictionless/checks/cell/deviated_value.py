import statistics
from ...check import Check
from ... import errors


DEFAULT_INTERVAL = 3
DEFAULT_AVERAGE = "mean"
AVERAGE_FUNCTIONS = {
    "mean": statistics.mean,
    "median": statistics.median,
    "mode": statistics.mode,
}


class deviated_value(Check):
    """Check for deviated values in a field"""

    code = "deviated-value"
    Errors = [errors.DeviatedValueError]

    def __init__(
        self,
        *,
        field_name: str,
        interval: int = DEFAULT_INTERVAL,
        average: str = DEFAULT_AVERAGE,
    ):
        self.field_name = field_name
        self.interval = interval
        self.average = average

    # Properties

    field_name: str
    """# TODO: add docs"""

    interval: int
    """# TODO: add docs"""

    average: str
    """# TODO: add docs"""

    def connect(self, resource):
        super().connect(resource)
        self.__cells = []
        self.__row_positions = []
        self.__average_function = AVERAGE_FUNCTIONS.get(self.average)

    # Validate

    def validate_start(self):
        numeric = ["integer", "number"]
        if self.field_name not in self.resource.schema.field_names:
            note = 'deviated value check requires field "%s" to exist'
            yield errors.CheckError(note=note % self.field_name)
        elif self.resource.schema.get_field(self.field_name).type not in numeric:
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
            self.__row_positions.append(row.row_position)
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
        for row_position, cell in zip(self.__row_positions, self.__cells):
            if not (minimum <= cell <= maximum):
                note = 'value "%s" in row at position "%s" and field "%s" is deviated "[%.2f, %.2f]"'
                note = note % (cell, row_position, self.field_name, minimum, maximum)
                yield errors.DeviatedValueError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["fieldName"],
        "properties": {
            "code": {},
            "fieldName": {"type": "string"},
            "interval": {"type": ["number", "null"]},
            "average": {"type": ["string", "null"]},
        },
    }
