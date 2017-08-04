# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('maximum-length-constraint', type='schema', context='body')
def maximum_length_constraint(errors, cells, row_number):
    for cell in cells:

        # Skip if cell is incomplete
        if not set(cell).issuperset(['number', 'header', 'field', 'value']):
            continue

        # TODO: remove this skip after
        # https://github.com/frictionlessdata/goodtables-py/issues/174
        if not cell['field'].constraints.get('maxLength'):
            continue

        # Check constraint
        valid = cell['field'].test_value(cell['value'], constraint='maxLength')

        # Add error
        if not valid:
            message = spec['errors']['maximum-length-constraint']['message']
            message = message.format(
                value=cell['value'],
                row_number=row_number,
                column_number=cell['number'],
                constraint=cell['field'].constraints['maxLength'])
            errors.append({
                'code': 'maximum-length-constraint',
                'message': message,
                'row-number': row_number,
                'column-number': cell['number'],
            })
