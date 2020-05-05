from itertools import zip_longest
from collections import OrderedDict


class Row(OrderedDict):
    def __init__(self, cells, *, column_names, line_number, row_number):

        # Set params
        self.__line_number = line_number
        self.__row_number = row_number
        self.__errors = []

        # Fill the dict
        super().__init__()
        fillvalue = '__fillvalue__'
        iterator = zip_longest(column_names, cells, fillvalue=fillvalue)
        for columnNumber, [columnName, cell] in enumerate(iterator, start=1):
            if columnName == fillvalue:
                columnName = 'column%s' % columnNumber
            if cell == fillvalue:
                break
            self[columnName] = cell

    @property
    def cells(self):
        return list(self.values())

    @property
    def column_names(self):
        return list(self.keys())

    @property
    def line_number(self):
        return self.__line_number

    @property
    def row_number(self):
        return self.__row_number

    @property
    def errors(self):
        return self.__errors

    def add_error(self, error):
        self.__errors.append(error)
