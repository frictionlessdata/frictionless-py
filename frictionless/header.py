from itertools import zip_longest
from .helpers import cached_property
from . import errors


class Header(list):
    """Header representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Header`

    Parameters:
        cells (any[]): header row cells
        schema (Schema): table schema
        field_positions (int[]): field positions

    """

    def __init__(self, cells, *, schema, field_positions, ignore_case=False):
        assert len(field_positions) in (len(cells), len(schema.fields))

        # Set attributes
        fields = schema.fields
        self.__schema = schema
        self.__field_positions = field_positions
        self.__errors = []

        # Extra header
        if len(fields) < len(cells):
            iterator = cells[len(fields) :]
            start = max(field_positions[: len(fields)]) + 1
            del cells[len(fields) :]
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraHeaderError(
                        note="",
                        cells=cells,
                        cell="",
                        field_name="",
                        field_number=len(fields) + field_position - start,
                        field_position=field_position,
                    )
                )

        # Missing header
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = zip_longest(field_positions[len(cells) :], fields[len(cells) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingHeaderError(
                            note="",
                            cells=list(map(str, cells)),
                            cell="",
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position
                            or max(field_positions, default=0) + field_number - start + 1,
                        )
                    )

        # Iterate items
        field_number = 0
        for field_position, field, cell in zip(field_positions, fields, cells):
            field_number += 1

            # Blank Header
            if not cell:
                self.__errors.append(
                    errors.BlankHeaderError(
                        note="",
                        cells=list(map(str, cells)),
                        cell="",
                        field_name=field.name,
                        field_number=field_number,
                        field_position=field_position,
                    )
                )

            # Duplicated Header
            if cell:
                duplicate_field_positions = []
                seen_cells = cells[0 : field_number - 1]
                seen_field_positions = field_positions[0 : field_number - 1]
                for seen_position, seen_cell in zip(seen_field_positions, seen_cells):
                    if cell == seen_cell:
                        duplicate_field_positions.append(seen_position)
                if duplicate_field_positions:
                    cell = None
                    note = 'at position "%s"'
                    note = note % ", ".join(map(str, duplicate_field_positions))
                    self.__errors.append(
                        errors.DuplicateHeaderError(
                            note=note,
                            cells=list(map(str, cells)),
                            cell=str(cells[field_number - 1]),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Non-matching Header
            if cell:
                name = field.name
                if name.lower() != cell.lower() if ignore_case else name != cell:
                    self.__errors.append(
                        errors.NonMatchingHeaderError(
                            note="",
                            cells=list(map(str, cells)),
                            cell=str(cell),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

        # Save header
        super().__init__(cells)

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
    def errors(self):
        """
        Returns:
            Error[]: header errors
        """
        return self.__errors

    @cached_property
    def valid(self):
        """
        Returns:
            bool: if header valid
        """
        return not self.__errors

    # Import/Export

    def to_dict(self):
        """Convert to a dict (field name -> header cell)"""
        result = {}
        for field, header in zip(self.__schema.fields, self):
            result[field.name] = header
        return result

    def to_list(self):
        """Convert to a list"""
        return list(self)
