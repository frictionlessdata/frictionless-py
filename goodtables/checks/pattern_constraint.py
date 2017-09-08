# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..registry import check


# Module API

@check('pattern-constraint', type='schema', context='body')
def pattern_constraint(errors, cells, row_number):
    for cell in copy(cells):

        # Skip if cell is incomplete
        if not set(cell).issuperset(['number', 'header', 'field', 'value']):
            continue

        # Check constraint
        valid = cell['field'].test_value(cell['value'], constraints=['pattern'])

        # Skip if valid
        if valid:
            continue

        # Add error
        message = spec['errors']['pattern-constraint']['message']
        message = message.format(
            value='"%s"' % cell['value'],
            row_number=row_number,
            column_number=cell['number'],
            constraint='"%s"' % cell['field'].constraints['pattern'])
        errors.append({
            'code': 'pattern-constraint',
            'message': message,
            'row-number': row_number,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
