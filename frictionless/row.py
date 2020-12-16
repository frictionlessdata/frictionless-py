# TODO: review this dependency
from .plugins.json import JsonParser
from itertools import zip_longest
from decimal import Decimal
from .helpers import cached_property
from . import helpers
from . import errors


class Row(list):
    """Row representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Row`

    > Constructor of this object is not Public API

    This object is returned by `extract`, `resource.read_rows`, and other functions.

    ```python
    rows = extract("data/table.csv")
    for row in rows:
        # work with the Row
    ```

    Parameters:
        cells (any[]): array of cells
        field_info (dict): special field info structure
        row_position (int): row position from 1
        row_number (int): row number from 1
    """

    def __init__(
        self,
        cells,
        *,
        field_info,
        row_position,
        row_number,
    ):
        self.extend(cells)
        self.__field_info = field_info
        self.__row_position = row_position
        self.__row_number = row_number
        self.__processed = False
        self.__blank_cells = {}
        self.__error_cells = {}
        self.__read_cells = {}
        self.__errors = []

    def __getitem__(self, key):
        if isinstance(key, str):
            if key not in self.__read_cells:
                return self.__process(key)
            return self.__read_cell[key]
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            # TODO: improve key error
            field, field_number, field_position = self.__field_info["mapping"][key]
            key = field_number
        return super().__setitem__(key, value)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self.__field_info["mapping"]
        return super().__contains__(key)

    @cached_property
    def fields(self):
        """
        Returns:
            Field[]: table schema fields
        """
        return self.__field_info["objects"]

    @cached_property
    def field_names(self):
        """
        Returns:
            Schema: table schema
        """
        return self.__field_info["names"]

    @cached_property
    def field_positions(self):
        """
        Returns:
            int[]: table field positions
        """
        return self.__field_info["positions"]

    @cached_property
    def row_position(self):
        """
        Returns:
            int: row position from 1
        """
        return self.__row_position

    @cached_property
    def row_number(self):
        """
        Returns:
            int: row number from 1
        """
        return self.__row_number

    @cached_property
    def blank_cells(self):
        """A mapping indexed by a field name with blank cells before parsing

        Returns:
            dict: row blank cells
        """
        self.__process()
        return self.__blank_cells

    @cached_property
    def error_cells(self):
        """A mapping indexed by a field name with error cells before parsing

        Returns:
            dict: row error cells
        """
        self.__process()
        return self.__error_cells

    @cached_property
    def errors(self):
        """
        Returns:
            Error[]: row errors
        """
        self.__process()
        return self.__errors

    @cached_property
    def valid(self):
        """
        Returns:
            bool: if row valid
        """
        self.__process()
        return not self.__errors

    # Import/Export

    def to_str(self):
        """
        Returns:
            str: a row as a CSV string
        """
        cells = []
        for field in self.__field_info["fields"]:
            cell, notes = field.write_cell(self[field.name])
            cells.append(cell)
        return helpers.stringify_csv_string(cells)

    def to_dict(self, *, json=False):
        """
        Parameters:
            json (bool): make data types compatible with JSON format

        Returns:
            dict: a row as a dictionary
        """
        # TODO: change in-place
        if json:
            result = {}
            for field in self.__field_info["fields"]:
                cell = self[field.name]
                if field.type not in JsonParser.native_types:
                    cell, notes = field.write_cell(cell, ignore_missing=True)
                if isinstance(cell, Decimal):
                    cell = float(cell)
                result[field.name] = cell
            return result
        self.__process()
        return self.__read_cells.copy()

    def to_list(self, *, json=False):
        """
        Parameters:
            json (bool): make data types compatible with JSON format

        Returns:
            dict: a row as a list
        """
        # TODO: change in-place
        if json:
            result = []
            for field in self.__field_info["fields"]:
                cell = self[field.name]
                if field.type not in JsonParser.native_types:
                    cell, notes = field.write_cell(cell, ignore_missing=True)
                if isinstance(cell, Decimal):
                    cell = float(cell)
                result.append(cell)
            return result
        self.__process()
        return list(self.__read_cells.values())

    # Process

    def __process(self, key=None):

        # Exit if processed
        if self.__processed:
            if key:
                raise KeyError(key)
            return

        # Prepare context
        fields = self.__field_info["objects"]
        field_positions = self.__field_info["positions"]
        iterator = zip(self.__field_info["mapping"].values(), self)
        if key:
            field, field_num, field_pos = self.__field_info["mapping"][key]
            iterator = zip([(field, field_num, field_pos)], [self[field_num - 1]])

        # Iterate cells
        for (field, field_number, field_position), source in iterator:

            # Read cell
            target, notes = field.read_cell(source)
            type_note = notes.pop("type", None) if notes else None
            if target is None and not type_note:
                self.__blank_cells[field.name] = source

            # Type error
            if type_note:
                self.__error_cells[field.name] = source
                self.__errors.append(
                    errors.TypeError(
                        note=type_note,
                        cells=list(map(str, self)),
                        row_number=self.__row_number,
                        row_position=self.__row_position,
                        cell=str(source),
                        field_name=field.name,
                        field_number=field_number,
                        field_position=field_position,
                    )
                )

            # Constraint errors
            if notes:
                for note in notes.values():
                    self.__errors.append(
                        errors.ConstraintError(
                            note=note,
                            cells=list(map(str, self)),
                            row_number=self.__row_number,
                            row_position=self.__row_position,
                            cell=str(source),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Set/return value
            self.__read_cells[field.name] = target
            if key:
                return target

        # Extra cells
        if len(fields) < len(self):
            iterator = self[len(fields) :]
            start = max(field_positions[: len(fields)]) + 1
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraCellError(
                        note="",
                        cells=list(map(str, self)),
                        row_number=self.__row_number,
                        row_position=self.__row_position,
                        cell=str(cell),
                        field_name="",
                        field_number=len(fields) + field_position - start,
                        field_position=field_position,
                    )
                )

        # Missing cells
        if len(fields) > len(self):
            start = len(self) + 1
            iterator = zip_longest(field_positions[len(self) :], fields[len(self) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingCellError(
                            note="",
                            cells=list(map(str, self)),
                            row_number=self.__row_number,
                            row_position=self.__row_position,
                            cell="",
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position
                            or max(field_positions) + field_number - start + 1,
                        )
                    )

        # Blank row
        if len(fields) == len(self.__blank_cells):
            self.__errors = [
                errors.BlankRowError(
                    note="",
                    cells=list(map(str, self)),
                    row_number=self.__row_number,
                    row_position=self.__row_position,
                )
            ]

        # Set processed
        self.__processed = True
