# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('extra-value')
class ExtraValue(object):
    def __init__(self, **options):
        self._num_columns = None

    def check_row(self, cells):
        errors = []

        # Check that all rows have the same number of columns
        if self._num_columns is None:
            self._num_columns = len(cells)
        elif len(cells) > self._num_columns:
            extra_cells = cells[self._num_columns:]
            for cell in extra_cells:
                error = Error('extra-value', cell)
                errors.append(error)
                cells.remove(cell)
            return errors

        # Check that if any cell has a header, all cells MUST have headers as
        # well. This deals with the case of data files without headers.
        headers = [cell.get('header') for cell in cells]
        has_header = any(headers)
        # should report extra value when cell does not have header
        # and also has value in the cell
        cells_without_header = filter(lambda cell: cell.get('header') is None
                                      and cell.get('value'), cells)
        if has_header and cells_without_header:
            for cell in cells_without_header:
                error = Error('extra-value', cell)
                errors.append(error)
                cells.remove(cell)

        return errors
