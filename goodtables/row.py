from collections import OrderedDict
from . import helpers


# TODO: fixed the performance
class Row(OrderedDict):
    def __init__(
        self,
        cells,
        *,
        field_names,
        field_positions,
        missing_values,
        row_position,
        row_number,
    ):
        assert len(field_names) == len(field_positions)

        # Set params
        self.__field_positions = field_positions
        self.__row_position = row_position
        self.__row_number = row_number
        self.__deleted_cells = {}
        self.__missing_cells = []
        self.__extra_cells = []
        self.__blank_cells = {}
        self.__is_blank = True
        self.__errors = []

        # Set contents
        iterator = helpers.combine(field_names, cells)
        for field_number, [field_name, cell] in enumerate(iterator, start=1):
            if field_name == helpers.combine.missing:
                self.__extra_cells.append(cell)
                continue
            if cell == helpers.combine.missing:
                self.__missing_cells.append(field_name)
                cell = None
            if cell in missing_values:
                self.__blank_cells[field_name] = cell
                cell = None
            if cell is not None:
                self.__is_blank = False
            super().__setitem__(field_name, cell)

    def __setitem__(self, field_name, cell):
        if field_name not in self:
            raise KeyError(field_name)
        if cell is None and self[field_name] is not None:
            self.__deleted_cells[field_name] = self[field_name]
        super().__setitem__(field_name, cell)

    def __delitem__(self, field_name):
        self[field_name] = None

    def items_with_position(self):
        iterator = zip(self.__field_positions, self.items())
        return (
            (field_position, field_name, cell)
            for field_position, [field_name, cell] in iterator
        )

    @property
    def deleted_cells(self):
        return self.__deleted_cells

    @property
    def missing_cells(self):
        return self.__missing_cells

    @property
    def extra_cells(self):
        return self.__extra_cells

    @property
    def blank_cells(self):
        return self.__blank_cells

    @property
    def field_positions(self):
        return self.__field_positions

    @property
    def row_position(self):
        return self.__row_position

    @property
    def row_number(self):
        return self.__row_number

    @property
    def is_blank(self):
        return self.__is_blank

    @property
    def errors(self):
        return self.__errors

    def add_error(self, error):
        self.__errors.append(error)
