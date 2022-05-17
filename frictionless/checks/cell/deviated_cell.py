import statistics
from ... import errors
from ...check import Check
from typing import List, Iterator


class deviated_cell(Check):
    """Check if the cell size is deviated

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "deviated-cell", **descriptor}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       ignore_fields? (str[]): list of field names to ignore
       interval? (int): statistical interval (default: 3)

    """

    code = "deviated-cell"
    Errors = [errors.DeviatedCellError]

    def __init__(
        self, descriptor=None, *, ignore_fields: List[str] = None, interval: int = None
    ):
        self.setinitial("ignoreFields", ignore_fields)
        self.setinitial("interval", interval)
        super().__init__(descriptor)
        self.__cell_sizes = {}
        self.__fields = {}
        self.__ignore_fields = self.get("ignoreFields")
        self.__interval = self.get("interval", 3)

    def validate_row(self, row: any) -> Iterator:
        for field_idx, field in enumerate(row.fields):
            cell = row[field.name]
            if self.__ignore_fields and field.name in self.__ignore_fields:
                continue
            if cell and field.type == "string":
                if field_idx not in self.__cell_sizes:
                    self.__cell_sizes[field_idx] = {}
                self.__cell_sizes[field_idx][row.row_position] = len(cell) if cell else 0
                self.__fields[field_idx] = field.name
        yield from []

    def validate_end(self) -> Iterator:
        for field_idx, col_cell_sizes in self.__cell_sizes.items():
            threshold = 5000
            if len(col_cell_sizes) < 2:
                continue
            # Prepare maximum value
            try:
                stdev = statistics.stdev(col_cell_sizes.values())
                average = statistics.median(col_cell_sizes.values())
                maximum = average + stdev * self.__interval
            except Exception as exception:
                note = 'calculation issue "%s"' % exception
                yield errors.DeviatedCellError(note=note)
            # Use threshold or maximum value whichever is higher
            threshold = threshold if threshold > maximum else maximum
            for row_position, cell in col_cell_sizes.items():
                if cell > threshold:
                    note = 'cell at row "%s" and field "%s" has deviated size'
                    note = note % (row_position, self.__fields[field_idx])
                    yield errors.DeviatedCellError(note=note)

    # Metadata

    metadata_profile = {
        "type": "object",
        "properties": {
            "ignore_fields": {"type": ["string", "null"]},
            "interval": {"type": ["number", "null"]},
        },
    }
