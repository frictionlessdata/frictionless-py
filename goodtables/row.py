import tableschema
from collections import OrderedDict
from cached_property import cached_property
from . import errors


class Row(OrderedDict):
    def __init__(self, cells, *, fields, field_positions, row_position, row_number):
        assert len(fields) == len(field_positions)

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
            start = max(field_positions) + 1
            del cells[len(fields) :]
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraCellError(
                        cell=str(cell),
                        cells=map(str, cells),
                        fieldPosition=field_position,
                        rowNumber=row_number,
                        rowPosition=row_position,
                    )
                )

        # Missing cells
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = zip(field_positions[len(cells) :], fields[len(cells) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.MissingCellError(
                        cells=map(str, cells),
                        fieldName=field.name,
                        fieldNumber=field_number,
                        fieldPosition=field_position,
                        rowNumber=row_number,
                        rowPosition=row_position,
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
                else:
                    is_blank = False

            # Error cell
            #  if cell is not None:
            #  try:
            #  cell = field.cast(cell)
            #  except tableschema.exceptions.CastError:
            #  self.__error_cells[field.name] = cell
            #  cell = None
            #  # TODO: add errors

            # Save cell
            self[field.name] = cell

        # Blank row
        if is_blank:
            self.__errors = [
                errors.BlankRowError(
                    cells=map(str, cells), rowNumber=row_number, rowPosition=row_position,
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
