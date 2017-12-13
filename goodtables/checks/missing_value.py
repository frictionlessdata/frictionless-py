# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('missing-value', type='structure', context='body')
def missing_value(cells, row_number):
    errors = []

    for cell in copy(cells):

        # Skip if value in cell
        if 'value' in cell:
            continue

        # Add error
        error = Error('missing-value', cell, row_number)
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
