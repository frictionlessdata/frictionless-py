# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('required-constraint')
def required_constraint(cells):
    errors = []

    for cell in copy(cells):

        field = cell.get('field')
        value = cell.get('value')

        # Skip if cell has no field
        if field is None:
            continue

        # Check constraint
        valid = field.test_value(value, constraints=['required'])
        if field.descriptor.get('primaryKey'):
            valid = valid and field.cast_value(value) is not None

        # Skip if valid
        if valid:
            continue

        # Add error

        error = Error('required-constraint', cell)
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
