from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass, field
from ..metadata2 import Metadata2
from .describe import describe
from .validate import validate
from ..control import Control
from .. import settings
from .. import helpers
from .. import errors


# TODO: provide helpers properties like `dialect.csv`?
@dataclass
class Dialect(Metadata2):
    """Dialect representation"""

    describe = describe
    validate = validate

    # Properties

    header: bool = settings.DEFAULT_HEADER
    """TODO: add docs"""

    header_rows: List[int] = field(default_factory=lambda: settings.DEFAULT_HEADER_ROWS)
    """TODO: add docs"""

    header_join: str = settings.DEFAULT_HEADER_JOIN
    """TODO: add docs"""

    header_case: bool = settings.DEFAULT_HEADER_CASE
    """TODO: add docs"""

    comment_char: Optional[str] = None
    """TODO: add docs"""

    comment_rows: List[int] = field(default_factory=list)
    """TODO: add docs"""

    null_sequence: Optional[str] = None
    """TODO: add docs"""

    controls: List[Control] = field(default_factory=list)
    """TODO: add docs"""

    # Controls

    def has_control(self, code: str):
        return bool(self.get_control(code))

    # TODO: rebase on create=True instead of ensure
    def get_control(
        self, code: str, *, ensure: Optional[Control] = None
    ) -> Optional[Control]:
        for control in self.controls:
            if control.code == code:
                return control
        if ensure:
            self.controls.append(ensure)
            return ensure

    # Read

    def read_labels(self, sample):

        # Collect lists
        lists = []
        row_number = 0
        for cells in sample:
            row_number += 1
            if row_number in self.header_rows:
                lists.append(helpers.stringify_label(cells))
            if row_number >= max(self.header_rows, default=0):
                break

        # No header
        if not self.header:
            return []

        # Get labels
        labels = []
        prev_cells = {}
        for cells in lists:
            for index, cell in enumerate(cells):
                if prev_cells.get(index) == cell:
                    continue
                prev_cells[index] = cell
                if len(labels) <= index:
                    labels.append(cell)
                    continue
                labels[index] = self.header_join.join([labels[index], cell])

        return labels

    def read_fragment(self, sample):

        # Collect fragment
        fragment = []
        row_number = 0
        fragment_positions = []
        for row_position, cells in enumerate(sample, start=1):
            row_number += 1
            if self.header:
                if self.header_rows and row_number < self.header_rows[0]:
                    continue
                if row_number in self.header_rows:
                    continue
            fragment_positions.append(row_position)
            fragment.append(cells)

        return fragment, fragment_positions

    # Metadata

    metadata_Error = errors.DialectError
    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "headerRows": {},
            "headerJoin": {},
            "headerCase": {},
            "controls": {},
        },
    }
