import statistics
from ... import errors
from ...check import Check


class outlier_value(Check):
    """Check for outlier values in a field

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "outlier-value", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       field_name (str): a field name to check
       interval? (str): statistical interval (default: 3)

    """

    code = "outlier-value"
    Errors = [errors.OutlierValueError]

    def __init__(self, descriptor=None, *, field_name=None, interval=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("interval", interval)
        super().__init__(descriptor)
        self.__cells = []
        self.__row_positions = []
        self.__field_name = self["fieldName"]
        self.__interval = self.get("interval", 3)

    # Validate

    def validate_start(self):
        if self.__field_name not in self.resource.schema.field_names:
            note = 'outlier value check requires field "%s" to exist'
            yield errors.CheckError(note=note % self.__field_name)
        elif self.resource.schema.get_field(self.__field_name).type != "string":
            note = 'outlier value check requires field "%s" to be string'
            yield errors.CheckError(note=note % self.__field_name)

    def validate_row(self, row):
        cell = row[self.__field_name]
        if cell is not None:
            self.__cells.append(len(cell))
            self.__row_positions.append(row.row_position)
        yield from []

    def validate_end(self):
        if len(self.__cells) < 2:
            return

        # Prepare interval
        try:
            stdev = statistics.stdev(self.__cells)
            average = statistics.median(self.__cells)
            minimum = average - stdev * self.__interval
            maximum = average + stdev * self.__interval
        except Exception as exception:
            note = 'calculation issue "%s"' % exception
            yield errors.OutlierValueError(note=note)

        # Check values
        for i, (row_position, cell) in enumerate(zip(self.__row_positions, self.__cells)):
            if not (minimum <= cell <= maximum):
                note = 'value in row at position "%s" and field "%s" is deviated'
                note = note % (row_position, self.__field_name)
                yield errors.OutlierValueError(note=note)

    # Metadata

    metadata_profile = {
        "type": "object",
        "requred": ["fieldName"],
        "properties": {"fieldName": {"type": "string"}},
    }
