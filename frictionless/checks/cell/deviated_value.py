import statistics
from ... import errors
from ...check import Check


class deviated_value(Check):
    """Check for deviated values in a field

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "deviated-value", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       field_name (str): a field name to check
       average? (str): one of "mean", "median" or "mode" (default: "mean")
       interval? (str): statistical interval (default: 3)

    """

    code = "deviated-value"
    Errors = [errors.DeviatedValueError]

    def __init__(self, descriptor=None, *, field_name=None, average=None, interval=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("average", average)
        self.setinitial("interval", interval)
        super().__init__(descriptor)
        self.__cells = []
        self.__row_positions = []
        self.__field_name = self["fieldName"]
        self.__interval = self.get("interval", 3)
        self.__average = self.get("average", "mean")
        self.__average_function = AVERAGE_FUNCTIONS.get(self.__average)

    # Validate

    def validate_start(self):
        numeric = ["integer", "number"]
        if self.__field_name not in self.resource.schema.field_names:
            note = 'deviated value check requires field "%s" to exist'
            yield errors.CheckError(note=note % self.__field_name)
        elif self.resource.schema.get_field(self.__field_name).type not in numeric:
            note = 'deviated value check requires field "%s" to be numiric'
            yield errors.CheckError(note=note % self.__field_name)
        if not self.__average_function:
            note = 'deviated value check supports only average functions "%s"'
            note = note % ", ".join(AVERAGE_FUNCTIONS.keys())
            yield errors.CheckError(note=note)

    def validate_row(self, row):
        cell = row[self.__field_name]
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
            average = self.__average_function(self.__cells)
            minimum = average - stdev * self.__interval
            maximum = average + stdev * self.__interval
        except Exception as exception:
            note = 'calculation issue "%s"' % exception
            yield errors.DeviatedValueError(note=note)

        # Check values
        for row_position, cell in zip(self.__row_positions, self.__cells):
            if not (minimum <= cell <= maximum):
                note = 'value "%s" in row at position "%s" and field "%s" is deviated "[%.2f, %.2f]"'
                note = note % (cell, row_position, self.__field_name, minimum, maximum)
                yield errors.DeviatedValueError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "requred": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "average": {"type": ["string", "null"]},
            "interval": {"type": ["number", "null"]},
        },
    }


# Internal


AVERAGE_FUNCTIONS = {
    "mean": statistics.mean,
    "median": statistics.median,
    "mode": statistics.mode,
}
