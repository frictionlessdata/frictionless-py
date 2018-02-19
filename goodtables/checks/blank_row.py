# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('blank-row')
def blank_row(cells):
    errors = []

    if not list(filter(lambda cell: cell.get('value'), cells)):

        # Add error
        error = Error('blank-row', row_number=cells[0].get('row-number'))
        errors.append(error)

        # Clear cells
        del cells[:]

    return errors
