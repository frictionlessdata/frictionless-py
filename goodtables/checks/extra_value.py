# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('extra-value', type='structure', context='body')
def extra_value(cells, row_number):
    errors = []

    for cell in copy(cells):

        # Skip if header in cell
        if 'header' in cell:
            continue

        # Add error
        error = Error('extra-value', cell, row_number)
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
