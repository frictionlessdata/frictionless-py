from itertools import zip_longest
from collections import OrderedDict
from cached_property import cached_property
from . import errors


class Row(OrderedDict):
    def __init__(self, cells, *, fields, field_positions, row_position, row_number):
        assert len(field_positions) in (len(cells), len(fields))

        # Set params
        self.__field_positions = field_positions
        self.__row_position = row_position
        self.__row_number = row_number
        self.__blank_cells = {}
        self.__error_cells = {}
        self.__errors = []

        # Extra cells
        if len(fields) < len(cells):
            iterator = cells[len(fields) :]
            start = max(field_positions[: len(fields)]) + 1
            del cells[len(fields) :]
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraCellError(
                        details='',
                        cells=list(map(str, cells)),
                        row_number=row_number,
                        row_position=row_position,
                        cell=str(cell),
                        field_name='',
                        field_number=len(fields) + field_position - start,
                        field_position=field_position,
                    )
                )

        # Missing cells
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = zip_longest(field_positions[len(cells) :], fields[len(cells) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                if field is not None:
                    cells.append(None)
                    self.__errors.append(
                        errors.MissingCellError(
                            details='',
                            cells=list(map(str, cells)),
                            row_number=row_number,
                            row_position=row_position,
                            cell='',
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position
                            or max(field_positions) + field_number - start + 1,
                        )
                    )

        # Iterate items
        is_blank = True
        field_number = 0
        for field_position, field, cell in zip(field_positions, fields, cells):
            field_number += 1

            # Blank cell
            if cell is not None:
                if cell in field.missing_values:
                    self.__blank_cells[field.name] = cell
                    cell = None

            # Required constraint
            if cell is None:
                if field.required:
                    self.__errors.append(
                        errors.RequiredError(
                            details='',
                            cells=list(map(str, cells)),
                            row_number=row_number,
                            row_position=row_position,
                            cell='',
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Type error
            if cell is not None:
                is_blank = False
                cell = field.cast_function(cell)
                if cell == field.ERROR:
                    cell = None
                    details = 'expected type is "%s" and format is "%s"'
                    details = details % (field.type, field.format)
                    self.__error_cells[field.name] = cell
                    self.__errors.append(
                        errors.TypeError(
                            details=details,
                            cells=list(map(str, cells)),
                            row_number=row_number,
                            row_position=row_position,
                            cell=str(cells[field_number - 1]),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Constraint errors
            if cell is not None:
                for name, check in field.check_functions.items():
                    if name not in ['required', 'unique']:
                        if not check(cell):
                            details = '"%s" is "%s"'
                            details = details % (field.constraints[name], name)
                            self.__errors.append(
                                errors.ConstraintError(
                                    details=details,
                                    cells=list(map(str, cells)),
                                    row_number=row_number,
                                    row_position=row_position,
                                    cell=str(cell),
                                    field_name=field.name,
                                    field_number=field_number,
                                    field_position=field_position,
                                )
                            )

            # Save cell
            self[field.name] = cell

        # Blank row
        if is_blank:
            self.__errors = [
                errors.BlankRowError(
                    details='',
                    cells=list(map(str, cells)),
                    row_number=row_number,
                    row_position=row_position,
                )
            ]

    @cached_property
    def field_positions(self):
        return self.__field_positions

    @cached_property
    def row_position(self):
        return self.__row_position

    @cached_property
    def row_number(self):
        return self.__row_number

    @cached_property
    def blank_cells(self):
        return self.__blank_cells

    @cached_property
    def error_cells(self):
        return self.__error_cells

    @cached_property
    def errors(self):
        return self.__errors
