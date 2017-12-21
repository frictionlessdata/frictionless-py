# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('missing-value')
def missing_value(cells):
    errors = []

    for cell in copy(cells):

        # Skip if cell has value
        if cell.get('value') is not None:
            continue

        # Add error
        error = Error('missing-value', cell)
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
