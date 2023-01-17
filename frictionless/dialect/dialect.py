from __future__ import annotations
import attrs
from typing import Optional, List, Any
from ..exception import FrictionlessException
from ..platform import platform
from ..metadata import Metadata
from .control import Control
from ..system import system
from .. import settings
from .. import helpers
from .. import errors


@attrs.define(kw_only=True)
class Dialect(Metadata):
    """Dialect representation"""

    # State

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Dialect.
    """

    description: Optional[str] = None
    """
    A brief description of the Dialect.
    """

    header: bool = settings.DEFAULT_HEADER
    """
    If true, the header will be read else header will be skipped.
    """

    header_rows: List[int] = attrs.field(factory=settings.DEFAULT_HEADER_ROWS.copy)
    """
    Specifies the row numbers for the header. Default is [1].
    """

    header_join: str = settings.DEFAULT_HEADER_JOIN
    """
    Separator to join text of two column's. The default value is " " and other values
    could be ":", "-" etc.
    """

    header_case: bool = settings.DEFAULT_HEADER_CASE
    """
    If set to false, it does case insensitive matching of header. The default value
    is True.
    """

    comment_char: Optional[str] = None
    """
    Specifies char used to comment the rows. The default value is None.
    For example: "#".
    """

    comment_rows: List[int] = attrs.field(factory=list)
    """
    A list of rows to ignore. For example: [1, 2]
    """

    skip_blank_rows: bool = False
    """
    Ignores rows if they are completely blank
    """

    controls: List[Control] = attrs.field(factory=list)
    """
    A list of controls which defines different aspects of reading data.
    """

    # Describe

    @staticmethod
    def describe(source: Optional[Any] = None, **options):
        """Describe the given source as a dialect

        Parameters:
            source (any): data source
            **options (dict): describe resource options

        Returns:
            Dialect: file dialect
        """
        resource = platform.frictionless.Resource.describe(source, **options)
        dialect = resource.dialect
        return dialect

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
        blank_filter = self.create_blank_filter()

        # Emit content stream
        for row_number, cells in enumerate(cell_stream, start=1):
            if row_number < first_content_row:
                continue
            if comment_filter:
                if not comment_filter(row_number, cells):
                    continue
            if blank_filter:
                if not blank_filter(cells):
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

    def create_blank_filter(self):
        if not self.skip_blank_rows:
            return None

        # Create filter
        def blank_filter(cells):
            for cell in cells:
                if cell not in [None, ""]:
                    return True
            return False

        return blank_filter

    # Metadata

    metadata_type = "dialect"
    metadata_Error = errors.DialectError
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array"},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
            "commentChar": {"type": "string"},
            "commentRows": {"type": "array"},
            "skipBlankRows": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "controls":
            return Control

    @classmethod
    def metadata_transform(cls, descriptor):
        super().metadata_transform(descriptor)

        # Csv (standards@1)
        for name in CSV_PROPS_V1:
            value = descriptor.pop(name, None)
            if value is not None:
                descriptor.setdefault("csv", {})
                descriptor["csv"][name] = value

    @classmethod
    def metadata_import(cls, descriptor, **options):
        dialect = super().metadata_import(descriptor, **options)

        # Controls
        for type, item in dialect.custom.items():
            if isinstance(item, dict):
                item["type"] = type
                control = Control.from_descriptor(item)
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

        # Csv (standards/v1)
        if system.standards == "v1":
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
