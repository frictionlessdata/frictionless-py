from __future__ import annotations
from typing import Optional, List
from importlib import import_module
from dataclasses import dataclass, field
from ..exception import FrictionlessException
from ..metadata import Metadata
from .control import Control
from .. import settings
from .. import helpers
from .. import errors


# TODO: provide helpers properties like `dialect.csv`?
@dataclass
class Dialect(Metadata):
    """Dialect representation"""

    # State

    header: bool = settings.DEFAULT_HEADER
    """TODO: add docs"""

    header_rows: List[int] = field(default_factory=settings.DEFAULT_HEADER_ROWS.copy)
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

    # Describe

    @staticmethod
    def describe(source, **options):
        """Describe the given source as a dialect

        Parameters:
            source (any): data source
            **options (dict): describe resource options

        Returns:
            Dialect: file dialect
        """
        Resource = import_module("frictionless").Resource
        resource = Resource.describe(source, **options)
        dialect = resource.dialect
        return dialect

    # Controls

    def add_control(self, control: Control) -> None:
        """Add new control to the schema"""
        self.controls.append(control)
        control.schema = self

    def has_control(self, code: str):
        """Check if control is present"""
        for control in self.controls:
            if control.code == code:
                return True
        return False

    # TODO: rebase on create=True instead of ensure?
    def get_control(self, code: str, *, ensure: Optional[Control] = None) -> Control:
        """Get control by code"""
        for control in self.controls:
            if control.code == code:
                return control
        if ensure:
            self.controls.append(ensure)
            return ensure
        error = errors.DialectError(note=f'control "{code}" does not exist')
        raise FrictionlessException(error)

    def set_control(self, control: Control) -> Optional[Control]:
        """Set control by code"""
        if self.has_control(control.code):
            prev_control = self.get_control(control.code)
            index = self.controls.index(prev_control)
            self.controls[index] = control
            control.schema = self
            return prev_control
        self.add_control(control)

    # Read

    def read_labels(self, sample):
        first_content_row = self.create_first_content_row()
        comment_filter = self.create_comment_filter()

        # Collect lists
        lists = []
        for row_number, cells in enumerate(sample, start=1):
            if comment_filter:
                if not comment_filter(row_number, cells):
                    continue
            if self.header:
                if row_number in self.header_rows:
                    lists.append(helpers.stringify_label(cells))
            if row_number >= first_content_row:
                break

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
        for _, cells in self.read_enumerated_content_stream(sample):
            fragment.append(cells)

        return fragment

    def read_enumerated_content_stream(self, list_stream):
        first_content_row = self.create_first_content_row()
        comment_filter = self.create_comment_filter()

        # Emit content stream
        for row_number, cells in enumerate(list_stream, start=1):
            if row_number < first_content_row:
                continue
            if comment_filter:
                if not comment_filter(row_number, cells):
                    continue
            yield (row_number, cells)

    # Filter

    def create_first_content_row(self):
        if self.header and self.header_rows:
            return self.header_rows[-1] + 1
        return 1

    def create_comment_filter(self):
        if not self.comment_char and not self.comment_rows:
            return None

        # Create filter
        def comment_filter(row_number, cells):
            if self.comment_char:
                if cells and str(cells[0]).startswith(self.comment_char):
                    return False
            if self.comment_rows:
                if row_number in self.comment_rows:
                    return False
            return True

        return comment_filter

    # Metadata

    metadata_Error = errors.DialectError
    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "header": {},
            "headerRows": {},
            "headerJoin": {},
            "headerCase": {},
            "commentChar": {},
            "commentRows": {},
            "nullSequence": {},
            "controls": {},
        },
    }

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(controls=Control)
