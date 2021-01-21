import hashlib
import statistics
from .. import errors
from ..check import Check


class duplicate_row(Check):
    """Check for duplicate rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "duplicate-row"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    code = "duplicate-row"
    Errors = [errors.DuplicateRowError]

    def prepare(self):
        self.__memory = {}

    def validate_row(self, row):
        text = ",".join(map(str, row.values()))
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        match = self.__memory.get(hash)
        if match:
            note = 'the same as row at position "%s"' % match
            yield errors.DuplicateRowError.from_row(row, note=note)
        self.__memory[hash] = row.row_position

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }


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

    def prepare(self):
        self.__exited = False
        self.__cells = []
        self.__row_positions = []
        self.__field_name = self["fieldName"]
        self.__interval = self.get("interval", 3)
        self.__average = self.get("average", "mean")
        self.__average_function = AVERAGE_FUNCTIONS.get(self.__average)

    # Validate

    def validate_task(self):
        numeric = ["integer", "number"]
        if self.__field_name not in self.table.schema.field_names:
            note = 'deviated value check requires field "%s" to exist'
            yield errors.TaskError(note=note % self.__field_name)
        elif self.table.schema.get_field(self.__field_name).type not in numeric:
            note = 'deviated value check requires field "%s" to be numiric'
            yield errors.TaskError(note=note % self.__field_name)
        if not self.__average_function:
            note = 'deviated value check supports only average functions "%s"'
            note = note % ", ".join(AVERAGE_FUNCTIONS.keys())
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell = row[self.__field_name]
        if cell is not None:
            self.__cells.append(cell)
            self.__row_positions.append(row.row_position)
        yield from []

    def validate_table(self):
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
                dtl = 'value "%s" in row at position "%s" and field "%s" is deviated "[%.2f, %.2f]"'
                dtl = dtl % (cell, row_position, self.__field_name, minimum, maximum)
                yield errors.DeviatedValueError(note=dtl)

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


class truncated_value(Check):
    """Check for possible truncated values

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "truncated-value"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    code = "truncated-value"
    Errors = [errors.TruncatedValueError]

    def validate_row(self, row):
        for field_name, cell in row.items():
            truncated = False
            if cell is None:
                continue

            # Check string cutoff
            if isinstance(cell, str):
                if len(cell) in TRUNCATED_STRING_LENGTHS:
                    truncated = True

            # Check integer cutoff
            if isinstance(cell, int):
                if cell in TRUNCATED_INTEGER_VALUES:
                    truncated = True

            # Add error
            if truncated:
                note = "value  is probably truncated"
                yield errors.TruncatedValueError.from_row(
                    row, note=note, field_name=field_name
                )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }


# Internal


AVERAGE_FUNCTIONS = {
    "mean": statistics.mean,
    "median": statistics.median,
    "mode": statistics.mode,
}
TRUNCATED_STRING_LENGTHS = [
    255,
]
TRUNCATED_INTEGER_VALUES = [
    # BigInt
    18446744073709551616,
    9223372036854775807,
    # Int
    4294967295,
    2147483647,
    # SummedInt
    2097152,
    # SmallInt
    65535,
    32767,
]
