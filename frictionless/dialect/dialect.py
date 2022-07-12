from __future__ import annotations
from typing import Optional, List
from importlib import import_module
from dataclasses import dataclass, field
from ..exception import FrictionlessException
from ..metadata import Metadata
from .control import Control
from ..system import system
from .. import settings
from .. import helpers
from .. import errors


@dataclass
class Dialect(Metadata):
    """Dialect representation"""

    # State

    name: Optional[str] = None
    """TODO: add docs"""

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

    # Validate

    def validate(self):
        timer = helpers.Timer()
        errors = self.metadata_errors
        Report = import_module("frictionless").Report
        return Report.from_validation(time=timer.time, errors=errors)

    # Controls

    def add_control(self, control: Control) -> None:
        """Add new control to the schema"""
        if self.has_control(control.type):
            error = errors.DialectError(note=f'control "{control.type}" already exists')
            raise FrictionlessException(error)
        self.controls.append(control)
        control.schema = self

    def has_control(self, type: str):
        """Check if control is present"""
        for control in self.controls:
            if control.type == type:
                return True
        return False

    def get_control(self, type: str) -> Control:
        """Get control by type"""
        for control in self.controls:
            if control.type == type:
                return control
        error = errors.DialectError(note=f'control "{type}" does not exist')
        raise FrictionlessException(error)

    def set_control(self, control: Control) -> Optional[Control]:
        """Set control by type"""
        if self.has_control(control.type):
            prev_control = self.get_control(control.type)
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

    def read_enumerated_content_stream(self, cell_stream):
        first_content_row = self.create_first_content_row()
        comment_filter = self.create_comment_filter()

        # Emit content stream
        for row_number, cells in enumerate(cell_stream, start=1):
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
                if cells and isinstance(cells[0], str):
                    if cells[0].startswith(self.comment_char):
                        return False
            if self.comment_rows:
                if row_number in self.comment_rows:
                    return False
            return True

        return comment_filter

    # Metadata

    metadata_Error = errors.DialectError
    metadata_Types = dict(controls=Control)
    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "name": {"type": "string"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array"},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
            "commentChar": {"type": "string"},
            "commentRows": {"type": "array"},
            "nullSequence": {"type": "string"},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        descriptor = super().metadata_normalize(descriptor)

        # Csv (v1)
        for name in CSV_PROPS_V1:
            value = descriptor.pop(name, None)
            if value is not None:
                descriptor.setdefault("csv", {})
                descriptor["csv"][name] = value

        # Controls
        dialect = super().metadata_import(descriptor)
        for type, descriptor in dialect.custom.items():
            if isinstance(descriptor, dict):
                descriptor["type"] = type
                control = Control.from_descriptor(descriptor)
                dialect.add_control(control)

        return dialect

    def metadata_export(self):
        descriptor = super().metadata_export()

        # Controls
        for control in self.controls:
            control_descriptor = control.to_descriptor()
            type = control_descriptor.pop("type")
            if control_descriptor:
                descriptor[type] = control_descriptor

        # Csv (v1)
        if system.standards_version == "v1":
            for name, value in descriptor.pop("csv", {}).items():
                descriptor[name] = value

        return descriptor


# Internal

CSV_PROPS_V1 = [
    "delimiter",
    "lineTerminator",
    "quoteChar",
    "doubleQuote",
    "escapeChar",
    "nullSequence",
    "skipInitialSpace",
]
