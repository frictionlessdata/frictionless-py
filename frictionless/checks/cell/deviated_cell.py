from __future__ import annotations

import statistics
from typing import TYPE_CHECKING, Dict, Iterable, List

import attrs

from ... import errors
from ...checklist import Check

if TYPE_CHECKING:
    from ...error import Error
    from ...resource import Resource
    from ...table import Row


DEFAULT_INTERVAL = 3


@attrs.define(kw_only=True, repr=False)
class deviated_cell(Check):
    """Check if the cell size is deviated"""

    type = "deviated-cell"
    Errors = [errors.DeviatedCellError]

    interval: int = DEFAULT_INTERVAL
    """
    Interval specifies number of standard deviation away from the center.
    The median is used to find the center of the data. The default value
    is 3.
    """

    ignore_fields: List[str] = attrs.field(factory=list)
    """
    List of data columns to be skipped by check. To all the data columns
    listed here, check will not be applied. The default value is [].
    """

    # Connect

    def connect(self, resource: Resource):
        super().connect(resource)
        self.__cell_sizes: Dict[int, Dict[int, int]] = {}
        self.__fields: Dict[int, str] = {}

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

    metadata_profile_patch = {
        "properties": {
            "interval": {"type": "number"},
            "ignoreFields": {"type": "array"},
        },
    }
