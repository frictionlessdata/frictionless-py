from itertools import zip_longest
from collections import OrderedDict
from . import helpers


class Row(OrderedDict):
    def __init__(self, cells, *, field_names, line_number, row_number):

        # TODO: how to handle column_number?

        # Set params
        self.__line_number = line_number
        self.__row_number = row_number
        self.__deletions = {}
        self.__errors = []
        self.__ready = False

        # Set contents
        iterator = helpers.combine(field_names, cells)
        for field_number, [field_name, cell] in enumerate(iterator, start=1):
            if field_name == helpers.combine.missing:
                field_name = 'field%s' % field_number
            if cell == helpers.combine.missing:
                break
            self[field_name] = cell
        self.__ready = True

    def __setitem__(self, field_name, cell):
        if self.__ready:
            if field_name not in self:
                raise KeyError(field_name)
            if cell is None and self[field_name] is not None:
                self.__deletions[field_name] = self[field_name]
        super().__setitem__(field_name, cell)

    def __delitem__(self, field_name):
        self[field_name] = None

    @property
    def cells(self):
        return list(self.values())

    @property
    def field_names(self):
        return list(self.keys())

    @property
    def line_number(self):
        return self.__line_number

    @property
    def row_number(self):
        return self.__row_number

    @property
    def deletions(self):
        return self.__deletions

    @property
    def errors(self):
        return self.__errors

    def add_error(self, error):
        self.__errors.append(error)
