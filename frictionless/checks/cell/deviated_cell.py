from __future__ import annotations
import statistics
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Iterable
from ...check import Check
from ... import errors

if TYPE_CHECKING:
    from ...row import Row
    from ...error import Error


DEFAULT_INTERVAL = 3


@dataclass
class deviated_cell(Check):
    """Check if the cell size is deviated"""

    code = "deviated-cell"
    Errors = [errors.DeviatedCellError]

    # Properties

    interval: int = DEFAULT_INTERVAL
    """# TODO: add docs"""

    ignore_fields: List[str] = field(default_factory=list)
    """# TODO: add docs"""

    # Connect

    def connect(self, resource):
        super().connect(resource)
        self.__cell_sizes = {}
        self.__fields = {}

    # Validate

    def validate_row(self, row: Row) -> Iterable[Error]:
        for field_idx, field in enumerate(row.fields):  # type: ignore
            cell = row[field.name]
            if self.ignore_fields and field.name in self.ignore_fields:
                continue
            if cell and field.type == "string":
                if field_idx not in self.__cell_sizes:
                    self.__cell_sizes[field_idx] = {}
                self.__cell_sizes[field_idx][row.row_number] = len(cell) if cell else 0
                self.__fields[field_idx] = field.name
        yield from []

    def validate_end(self) -> Iterable[Error]:
        for field_idx, col_cell_sizes in self.__cell_sizes.items():
            threshold = 5000
            if len(col_cell_sizes) < 2:
                continue
            # Prepare maximum value
            try:
                stdev = statistics.stdev(col_cell_sizes.values())
                average = statistics.median(col_cell_sizes.values())
                maximum = average + stdev * self.interval
                # Use threshold or maximum value whichever is higher
                threshold = threshold if threshold > maximum else maximum
                for row_number, cell in col_cell_sizes.items():
                    if cell > threshold:
                        note = 'cell at row "%s" and field "%s" has deviated size'
                        note = note % (row_number, self.__fields[field_idx])
                        yield errors.DeviatedCellError(note=note)
            except Exception as exception:
                note = 'calculation issue "%s"' % exception
                yield errors.DeviatedCellError(note=note)

    # Metadata

    metadata_profile = {
        "type": "object",
        "properties": {
            "code": {},
            "interval": {"type": "number"},
            "ignoreFields": {"type": "array"},
        },
    }
