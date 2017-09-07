# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('minimum-constraint', type='schema', context='body')
def minimum_constraint(errors, cells, row_number):
    for cell in cells:

        # Skip if cell is incomplete
        if not set(cell).issuperset(['number', 'header', 'field', 'value']):
            continue

        # Check constraint
        valid = cell['field'].test_value(cell['value'], constraints=['minimum'])

        # Add error
        if not valid:
            message = spec['errors']['minimum-constraint']['message']
            message = message.format(
                value='"%s"' % cell['value'],
                row_number=row_number,
                column_number=cell['number'],
                constraint='"%s"' % cell['field'].constraints['minimum'])
            errors.append({
                'code': 'minimum-constraint',
                'message': message,
                'row-number': row_number,
                'column-number': cell['number'],
            })
