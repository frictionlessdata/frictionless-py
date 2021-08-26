import typing
from .metadata import Metadata
from . import settings
from . import helpers
from . import errors


class Layout(Metadata):
    """Layout representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Layout`

    Parameters:
        descriptor? (str|dict): layout descriptor
        pick_fields? ((str|int)[]): what fields to pick
        skip_fields? ((str|int)[]): what fields to skip
        limit_fields? (int): amount of fields
        offset_fields? (int): from what field to start
        pick_rows? ((str|int)[]): what rows to pick
        skip_rows? ((str|int)[]): what rows to skip
        limit_rows? (int): amount of rows
        offset_rows? (int): from what row to start
    """

    def __init__(
        self,
        descriptor=None,
        *,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
        pick_fields=None,
        skip_fields=None,
        limit_fields=None,
        offset_fields=None,
        pick_rows=None,
        skip_rows=None,
        limit_rows=None,
        offset_rows=None,
    ):
        self.setinitial("header", header)
        self.setinitial("headerRows", header_rows)
        self.setinitial("headerJoin", header_join)
        self.setinitial("headerCase", header_case)
        self.setinitial("pickFields", pick_fields)
        self.setinitial("skipFields", skip_fields)
        self.setinitial("limitFields", limit_fields)
        self.setinitial("offsetFields", offset_fields)
        self.setinitial("pickRows", pick_rows)
        self.setinitial("skipRows", skip_rows)
        self.setinitial("limitRows", limit_rows)
        self.setinitial("offsetRows", offset_rows)
        super().__init__(descriptor)

    @Metadata.property
    def header(self):
        """
        Returns:
            bool: if there is a header row
        """
        return self.get("header", settings.DEFAULT_HEADER)

    @Metadata.property
    def header_rows(self):
        """
        Returns:
            int[]: header rows
        """
        if not self.header:
            return []
        return self.get("headerRows", settings.DEFAULT_HEADER_ROWS)

    @Metadata.property
    def header_join(self):
        """
        Returns:
            str: header joiner
        """
        return self.get("headerJoin", settings.DEFAULT_HEADER_JOIN)

    @Metadata.property
    def header_case(self):
        """
        Returns:
            str: header case sensitive
        """
        return self.get("headerCase", settings.DEFAULT_HEADER_CASE)

    @Metadata.property
    def pick_fields(self):
        """
        Returns:
            (str|int)[]?: pick fields
        """
        return self.get("pickFields")

    @Metadata.property
    def skip_fields(self):
        """
        Returns:
            (str|int)[]?: skip fields
        """
        return self.get("skipFields")

    @Metadata.property
    def limit_fields(self):
        """
        Returns:
            int?: limit fields
        """
        return self.get("limitFields")

    @Metadata.property
    def offset_fields(self):
        """
        Returns:
            int?: offset fields
        """
        return self.get("offsetFields")

    @Metadata.property
    def pick_rows(self):
        """
        Returns:
            (str|int)[]?: pick rows
        """
        return self.get("pickRows")

    @Metadata.property
    def skip_rows(self):
        """
        Returns:
            (str|int)[]?: skip rows
        """
        return self.get("skipRows")

    @Metadata.property
    def limit_rows(self):
        """
        Returns:
            int?: limit rows
        """
        return self.get("limitRows")

    @Metadata.property
    def offset_rows(self):
        """
        Returns:
            int?: offset rows
        """
        return self.get("offsetRows")

    @Metadata.property(write=False)
    def is_field_filtering(self):
        """
        Returns:
            bool: whether there is a field filtering
        """
        return (
            self.pick_fields is not None
            or self.skip_fields is not None
            or self.limit_fields is not None
            or self.offset_fields is not None
        )

    @Metadata.property(write=False)
    def pick_fields_compiled(self):
        """
        Returns:
            re?: compiled pick fields
        """
        return helpers.compile_regex(self.pick_fields)

    @Metadata.property(write=False)
    def skip_fields_compiled(self):
        """
        Returns:
            re?: compiled skip fields
        """
        return helpers.compile_regex(self.skip_fields)

    @Metadata.property(write=False)
    def pick_rows_compiled(self):
        """
        Returns:
            re?: compiled pick rows
        """
        return helpers.compile_regex(self.pick_rows)

    @Metadata.property(write=False)
    def skip_rows_compiled(self):
        """
        Returns:
            re?: compiled skip fields
        """
        return helpers.compile_regex(self.skip_rows)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("header", self.header)
        self.setdefault("headerRows", self.header_rows)
        self.setdefault("headerJoin", self.header_join)
        self.setdefault("headerCase", self.header_case)

    # Read

    def read_labels(self, sample):

        # Collect lists
        lists = []
        row_number = 0
        for row_position, cells in enumerate(sample, start=1):
            if self.read_filter_rows(cells, row_position=row_position):
                row_number += 1
                if row_number in self.header_rows:
                    lists.append(helpers.stringify_label(cells))
                if row_number >= max(self.header_rows, default=0):
                    break

        # No header
        if not self.header:
            return [], list(range(1, len(sample[0]) + 1))

        # Get labels
        raw_labels = []
        prev_cells = {}
        for cells in lists:
            for index, cell in enumerate(cells):
                if prev_cells.get(index) == cell:
                    continue
                prev_cells[index] = cell
                if len(raw_labels) <= index:
                    raw_labels.append(cell)
                    continue
                raw_labels[index] = self.header_join.join([raw_labels[index], cell])

        # Filter labels
        labels = []
        field_positions = []
        limit = self.limit_fields
        offset = self.offset_fields or 0
        for field_position, label in enumerate(raw_labels, start=1):
            if self.read_filter_fields(label, field_position=field_position):
                if offset:
                    offset -= 1
                    continue
                labels.append(label)
                field_positions.append(field_position)
                if limit and limit <= len(labels):
                    break

        return labels, field_positions

    def read_fragment(self, sample):

        # Collect fragment
        fragment = []
        row_number = 0
        fragment_positions = []
        field_positions = self.read_labels(sample)[1]
        for row_position, cells in enumerate(sample, start=1):
            if self.read_filter_rows(cells, row_position=row_position):
                row_number += 1
                if self.header_rows and row_number < self.header_rows[0]:
                    continue
                if row_number in self.header_rows:
                    continue
                cells = self.read_filter_cells(cells, field_positions=field_positions)
                fragment_positions.append(row_position)
                fragment.append(cells)

        return fragment, fragment_positions

    def read_filter_fields(self, label, *, field_position):
        match = True
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.pick_fields_compiled
            else:
                items = self.skip_fields_compiled
            if not items:
                continue
            match = match and name == "skip"
            for item in items:
                if item == "<blank>" and label == "":
                    match = not match
                elif isinstance(item, str) and item == label:
                    match = not match
                elif isinstance(item, int) and item == field_position:
                    match = not match
                elif isinstance(item, typing.Pattern) and item.match(label):
                    match = not match
        return match

    def read_filter_rows(self, cells, *, row_position):
        match = True
        cell = cells[0] if cells else None
        cell = "" if cell is None else str(cell)
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.pick_rows_compiled
            else:
                items = self.skip_rows_compiled
            if not items:
                continue
            match = match and name == "skip"
            for item in items:
                if item == "<blank>":
                    if not any(cell for cell in cells if cell not in ["", None]):
                        match = not match
                elif isinstance(item, str):
                    if item == cell or (item and cell.startswith(item)):
                        match = not match
                elif isinstance(item, int) and item == row_position:
                    match = not match
                elif isinstance(item, typing.Pattern) and item.match(cell):
                    match = not match
        return match

    def read_filter_cells(self, cells, *, field_positions):
        if self.is_field_filtering:
            result = []
            for field_position, cell in enumerate(cells, start=1):
                if field_position in field_positions:
                    result.append(cell)
            return result
        return cells

    # Metadata

    metadata_Error = errors.LayoutError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
            "pickFields": {"type": "array"},
            "skipFields": {"type": "array"},
            "limitFields": {"type": "number", "minimum": 1},
            "offsetFields": {"type": "number", "minimum": 1},
            "pickRows": {"type": "array"},
            "skipRows": {"type": "array"},
            "limitRows": {"type": "number", "minimum": 1},
            "offsetRows": {"type": "number", "minimum": 1},
        },
    }
