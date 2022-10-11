from __future__ import annotations
from itertools import zip_longest
from functools import cached_property
from ..platform import platform
from .. import helpers
from .. import errors


# NOTE:
# Currently dict.update/setdefault/pop/popitem/clear is not disabled (can be confusing)
# We can consider adding row.header property to provide more comprehensive API


# TODO: add types
class Row(dict):
    """Row representation

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
        row_number (int): row number from 1
    """

    def __init__(
        self,
        cells,
        *,
        field_info,
        row_number,
    ):
        self.__cells = cells
        self.__field_info = field_info
        self.__row_number = row_number
        self.__processed = False
        self.__blank_cells = {}
        self.__error_cells = {}
        self.__errors: list[errors.RowError] = []

    def __eq__(self, other):
        self.__process()
        return super().__eq__(other)

    def __str__(self):
        self.__process()
        return super().__str__()

    def __repr__(self):
        self.__process()
        return super().__repr__()

    def __setitem__(self, key, value):
        try:
            _, field_number, _, _ = self.__field_info["mapping"][key]
        except KeyError:
            raise KeyError(f"Row does not have a field {key}")
        if len(self.__cells) < field_number:
            self.__cells.extend([None] * (field_number - len(self.__cells)))
        self.__cells[field_number - 1] = value
        super().__setitem__(key, value)

    def __missing__(self, key):
        return self.__process(key)

    def __iter__(self):
        return iter(self.__field_info["names"])

    def __len__(self):
        return len(self.__field_info["names"])

    def __contains__(self, key):
        return key in self.__field_info["mapping"]

    def __reversed__(self):
        return reversed(self.__field_info["names"])

    def keys(self):
        return iter(self.__field_info["names"])

    def values(self):
        for name in self.__field_info["names"]:
            yield self[name]

    def items(self):
        for name in self.__field_info["names"]:
            yield (name, self[name])

    def get(self, key, default=None):
        if key not in self.__field_info["names"]:
            return default
        return self[key]

    @cached_property
    def cells(self):
        """
        Returns:
            Field[]: table schema fields
        """
        return self.__cells

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
            str[]: field names
        """
        return self.__field_info["names"]

    @cached_property
    def field_numbers(self):
        """
        Returns:
            str[]: field numbers
        """
        return list(range(1, len(self.__field_info["names"]) + 1))

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

    # Convert

    def to_str(self, **options):
        """
        Returns:
            str: a row as a CSV string
        """
        types = platform.frictionless_formats.CsvParser.supported_types
        cells = self.to_list(types=types)
        return helpers.stringify_csv_string(cells, **options)

    def to_list(self, *, json=False, types=None):
        """
        Parameters:
            json (bool): make data types compatible with JSON format
            types (str[]): list of supported types

        Returns:
            dict: a row as a list
        """

        # Prepare
        self.__process()
        result = [self[name] for name in self.__field_info["names"]]
        if types is None and json:
            types = platform.frictionless_formats.JsonParser.supported_types

        # Convert
        if types is not None:
            for index, field_mapping in enumerate(self.__field_info["mapping"].values()):
                field, _, _, cell_writer = field_mapping
                # Here we can optimize performance if we use a types mapping
                if field.type in types:
                    continue
                # NOTE: Move somehow to be in the json plugin
                if json is True and field.type == "number" and field.float_number:
                    continue
                cell = result[index]
                cell, _ = cell_writer(cell, ignore_missing=True)
                result[index] = cell

        # Return
        return result

    def to_dict(self, *, json=False, types=None):
        """
        Parameters:
            json (bool): make data types compatible with JSON format

        Returns:
            dict: a row as a dictionary
        """

        # Prepare
        self.__process()
        result = {name: self[name] for name in self.__field_info["names"]}
        if types is None and json:
            types = platform.frictionless_formats.JsonParser.supported_types

        # Covert
        if types is not None:
            for field_mapping in self.__field_info["mapping"].values():
                field, _, _, cell_writer = field_mapping
                # Here we can optimize performance if we use a types mapping
                if field.type not in types:
                    cell = result[field.name]
                    cell, _ = cell_writer(cell, ignore_missing=True)
                    result[field.name] = cell

        # Return
        return result

    # Process

    def __process(self, key=None):

        # NOTE:
        # This algorithm might be improved especially for some
        # scenarios like full processing after random access etc

        # Exit if processed
        if self.__processed:
            return

        # Prepare context
        cells = self.__cells
        to_str = lambda v: str(v) if v is not None else ""
        fields = self.__field_info["objects"]
        field_mapping = self.__field_info["mapping"]
        iterator = zip_longest(field_mapping.values(), cells)
        is_empty = not bool(super().__len__())
        if key:
            try:
                field, field_number, cell_reader, cell_writer = self.__field_info[
                    "mapping"
                ][key]
            except KeyError:
                raise KeyError(f"Row does not have a field {key}")
            cell = cells[field_number - 1] if len(cells) >= field_number else None
            iterator = zip([(field, field_number, cell_reader, cell_writer)], [cell])

        # Iterate cells
        for field_mapping, source in iterator:

            # Prepare context
            if field_mapping is None:
                break
            field, field_number, cell_reader, _ = field_mapping
            if not is_empty and super().__contains__(field.name):
                continue

            # Read cell
            target, notes = cell_reader(source)
            type_note = notes.pop("type", None) if notes else None
            if target is None and not type_note:
                self.__blank_cells[field.name] = source

            # Type error
            if type_note:
                self.__error_cells[field.name] = source
                self.__errors.append(
                    errors.TypeError(
                        note=type_note,
                        cells=list(map(to_str, cells)),
                        row_number=self.__row_number,
                        cell=str(source),
                        field_name=field.name,
                        field_number=field_number,
                    )
                )

            # Constraint errors
            if notes:
                for note in notes.values():
                    self.__errors.append(
                        errors.ConstraintError(
                            note=note,
                            cells=list(map(to_str, cells)),
                            row_number=self.__row_number,
                            cell=str(source),
                            field_name=field.name,
                            field_number=field_number,
                        )
                    )

            # Set/return value
            super().__setitem__(field.name, target)
            if key:
                return target

        # Extra cells
        if len(fields) < len(cells):
            start = len(fields) + 1
            iterator = cells[len(fields) :]
            for field_number, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraCellError(
                        note="",
                        cells=list(map(to_str, cells)),
                        row_number=self.__row_number,
                        cell=str(cell),
                        field_name="",
                        field_number=field_number,
                    )
                )

        # Missing cells
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = fields[len(cells) :]
            for field_number, field in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingCellError(
                            note="",
                            cells=list(map(to_str, cells)),
                            row_number=self.__row_number,
                            cell="",
                            field_name=field.name,
                            field_number=field_number,
                        )
                    )

        # Blank row
        if len(fields) == len(self.__blank_cells):
            self.__errors = [
                errors.BlankRowError(
                    note="",
                    cells=list(map(to_str, cells)),
                    row_number=self.__row_number,
                )
            ]

        # Set processed
        self.__processed = True
