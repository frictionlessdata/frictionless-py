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
    """
    missing-value: 	A row has less columns than the header.
    """
    errors = []

    for cell in copy(cells):

        # Skip if cell has value
        # There is a difference between:
        # - not having value at all - there is no `value` key
        # - having a value which is falsy (None, False, '', etc)
        # (so we don't use something like `if cell.get('value')`)
        if 'value' in cell:
            continue

        # Add error
        error = Error('missing-value', cell)
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
