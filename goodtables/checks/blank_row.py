# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('blank-row', type='structure', context='body')
def blank_row(cells, row_number):
    errors = []

    if not list(filter(lambda cell: cell.get('value'), cells)):

        # Add error
        error = Error('blank-row', row_number=row_number)
        errors.append(error)

        # Clear cells
        del cells[:]

    return errors
