from __future__ import annotations

from collections import OrderedDict
from functools import cached_property
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .. import errors, helpers
from ..platform import platform

# NOTE:
# Currently dict.update/setdefault/pop/popitem/clear is not disabled (can be confusing)
# We can consider adding row.header property to provide more comprehensive API

if TYPE_CHECKING:
    from ..schema.field import Field


# TODO: add types
class Row(Dict[str, Any]):
    """Row representation

    > Constructor of this object is not Public API

    It works like a lazy dictionary: dictionary values are only computed (see
    `__process` method) if needed.

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
        cells: List[Any],
        *,
        expected_fields: List[Field],
        row_number: int,
    ):
        self.__cells = cells
        self.__expected_fields: OrderedDict[str, Field] = OrderedDict(
            (f.name, f) for f in expected_fields
        )
        self.__row_number = row_number
        self.__processed: bool = False
        self.__blank_cells: Dict[str, Any] = {}
        self.__error_cells: Dict[str, Any] = {}
        self.__errors: list[errors.RowError] = []

    def __eq__(self, other: object):
        self.__process()
        return super().__eq__(other)

    def __str__(self):
        s = ""
        if not self.__processed:
            s = "Unprocessed: "
        return s + super().__str__()

    def __repr__(self):
        s = ""
        if not self.__processed:
            s = "Unprocessed: "
        return s + "Row" + super().__repr__()

    def __setitem__(self, key: str, value: Any):
        try:
            keys = [k for k in self.__expected_fields.keys()]
            field_number = keys.index(key) + 1
        except ValueError:
            raise KeyError(f"Row does not have a field {key}")

        if len(self.__cells) < field_number:
            self.__cells.extend([None] * (field_number - len(self.__cells)))
        self.__cells[field_number - 1] = value
        super().__setitem__(key, value)

    def __missing__(self, key: str):
        return self.__process(key)

    def __iter__(self):
        return iter(self.__expected_fields)

    def __len__(self):
        return len(self.__expected_fields)

    def __contains__(self, key: object):
        return key in self.__expected_fields

    def __reversed__(self):
        return reversed(self.__expected_fields.keys())

    def keys(self):
        return self.__expected_fields.keys()

    def values(self):  # type: ignore
        self.__process()
        for name in self.__expected_fields:
            yield self[name]

    def items(self):  # type: ignore
        self.__process()
        for name in self.__expected_fields:
            yield (name, self[name])

    def get(self, key: str, default: Optional[Any] = None):
        self.__process()
        if key not in self.__expected_fields:
            return default
        return self[key]

    @cached_property
    def cells(self):
        """
        Returns:
            Any[]: Table cell values
        """
        self.__process()
        return self.__cells

    @cached_property
    def fields(self):
        """
        Returns:
            Field[]: table schema fields
        """
        return [f.to_copy() for f in self.__expected_fields.values()]

    @cached_property
    def field_names(self) -> List[str]:
        """
        Returns:
            str[]: field names
        """
        return [k for k in self.__expected_fields]

    @cached_property
    def field_numbers(self):
        """
        Returns:
            str[]: field numbers
        """
        return list(range(1, len(self.__expected_fields) + 1))

    @cached_property
    def row_number(self) -> int:
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

    def to_str(self, **options: Any):
        """
        Returns:
            str: a row as a CSV string
        """
        types = platform.frictionless_formats.CsvParser.supported_types
        cells = self.to_list(types=types)
        return helpers.stringify_csv_string(cells, **options)

    def to_list(self, *, json: bool = False, types: Optional[List[str]] = None):
        """
        Parameters:
            json (bool): make data types compatible with JSON format
            types (str[]): list of supported types

        Returns:
            dict: a row as a list
        """

        # Prepare
        self.__process()
        result = [self[name] for name in self.field_names]
        if types is None and json:
            types = platform.frictionless_formats.JsonParser.supported_types

        # Convert
        if types is not None:
            field_names = self.field_names
            for index, field_name in enumerate(field_names):
                field = self.__expected_fields[field_name]
                cell_writer = field.create_cell_writer()

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

    def to_dict(
        self,
        *,
        csv: bool = False,
        json: bool = False,
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Parameters:
            json (bool): make data types compatible with JSON format

        Returns:
            dict: a row as a dictionary
        """

        # Prepare
        self.__process()
        result = {name: self[name] for name in self.__expected_fields}
        if types is None and json:
            types = platform.frictionless_formats.JsonParser.supported_types
        if types is None and csv:
            types = platform.frictionless_formats.CsvParser.supported_types

        # Convert
        if types is not None:
            field_names = self.field_names
            for field_name in field_names:
                field = self.__expected_fields[field_name]
                cell_writer = field.create_cell_writer()

                # Here we can optimize performance if we use a types mapping
                if field.type not in types:
                    cell = result[field.name]
                    cell, _ = cell_writer(cell, ignore_missing=True)
                    result[field.name] = cell

        # Return
        return result

    # Process

    def __process(self, key: Optional[str] = None):
        # NOTE:
        # This algorithm might be improved especially for some
        # scenarios like full processing after random access etc

        # Exit if processed
        if self.__processed:
            return

        # Prepare context
        cells = self.__cells
        to_str = lambda v: str(v) if v is not None else ""  # type: ignore
        fields = [f.to_copy() for f in self.__expected_fields.values()]

        iterator = zip_longest(range(len(fields)), self.__expected_fields.values(), cells)
        is_empty = not bool(super().__len__())

        if key:
            try:
                field = self.__expected_fields.get(key)
                field_index = self.field_names.index(key)
            except ValueError:
                raise KeyError(f"Row does not have a field {key}")

            cell = cells[field_index] if len(cells) >= field_index + 1 else None
            iterator = [(field_index, field, cell)]

        # Iterate cells
        for index, field, cell in iterator:
            # Prepare context
            if field is None:
                break
            cell_reader = field.create_cell_reader()

            if not is_empty and super().__contains__(field.name):
                continue

            # Read cell
            target, notes = cell_reader(cell)
            type_note = notes.pop("type", None) if notes else None
            if target is None and not type_note:
                self.__blank_cells[field.name] = cell

            # Type error
            if type_note:
                self.__error_cells[field.name] = cell
                self.__errors.append(
                    errors.TypeError(
                        note=type_note,
                        cells=list(map(to_str, cells)),  # type: ignore
                        row_number=self.__row_number,
                        cell=str(cell),
                        field_name=field.name,
                        field_number=index + 1,
                    )
                )

            # Constraint errors
            if notes:
                for note in notes.values():
                    self.__errors.append(
                        errors.ConstraintError(
                            note=note,
                            cells=list(map(to_str, cells)),  # type: ignore
                            row_number=self.__row_number,
                            cell=str(cell),
                            field_name=field.name,
                            field_number=index + 1,
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
            for field_index, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraCellError(
                        note="",
                        cells=list(map(to_str, cells)),  # type: ignore
                        row_number=self.__row_number,
                        cell=str(cell),
                        field_name="",
                        field_number=field_index,
                    )
                )

        # Missing cells
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = fields[len(cells) :]
            for field_index, field in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingCellError(
                            note="",
                            cells=list(map(to_str, cells)),  # type: ignore
                            row_number=self.__row_number,
                            cell="",
                            field_name=field.name,
                            field_number=field_index,
                        )
                    )

        # Blank row
        if len(fields) == len(self.__blank_cells):
            self.__errors = [
                errors.BlankRowError(
                    note="",
                    cells=list(map(to_str, cells)),  # type: ignore
                    row_number=self.__row_number,
                )
            ]

        # Set processed
        self.__processed = True
