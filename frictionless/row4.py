# TODO: review this dependency
from .plugins.json import JsonParser
from itertools import zip_longest
from decimal import Decimal
from .helpers import cached_property
from . import helpers
from . import errors


class Row4(list):
    """Row representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Table`

    This object is returned by `extract`, `table.read_rows`, and other functions.

    ```python
    rows = extract("data/table.csv")
    for row in rows:
        # work with the Row
    ```

    Parameters:
        cells (any[]): array of cells
        schema (Schema): table schema
        field_positions (int[]): table field positions
        row_position (int): row position from 1
        row_number (int): row number from 1

    """

    def __init__(
        self,
        cells,
        *,
        schema,
        field_map,
        field_positions,
        row_position,
        row_number,
    ):
        self.extend(cells)
        self.__schema = schema
        self.__field_map = field_map
        self.__field_positions = field_positions
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
            field, field_position, field_number = self.__field_map[key]
            key = field_number
        return super().__setitem__(key, value)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self.__field_map
        return super().__contains__(key)

    @cached_property
    def schema(self):
        """
        Returns:
            Schema: table schema
        """
        return self.__schema

    @cached_property
    def field_positions(self):
        """
        Returns:
            int[]: table field positions
        """
        return self.__field_positions

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
        for field in self.__schema.fields:
            if field.name in self:
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
        if json:
            result = {}
            for field in self.__schema.fields:
                if field.name in self:
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
        if json:
            result = []
            for field in self.__schema.fields:
                if field.name in self:
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
        fields = self.__schema.fields
        field_positions = self.__field_positions

        # Exit if processed
        if self.__processed:
            if key:
                raise KeyError(key)
            return

        # Iterate cells
        # TODO: improve
        field_number = 0
        iterator = zip(field_positions, fields, self)
        if key:
            field, field_position, field_number = self.__field_map[key]
            iterator = zip([field_position], [field], self[field_number-1])
            field_number = field_number -1
        for field_position, field, source in iterator:
            field_number += 1

            # Read cell
            # TODO: recover
            #  source = None
            #  if len(self) >= field_number:
            #  source = super().__getitem__(field_number - 1)
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
            iterator = cells[len(fields) :]
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
