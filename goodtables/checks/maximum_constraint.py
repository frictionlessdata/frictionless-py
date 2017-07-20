# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('maximum-constraint', type='schema', context='body')
def maximum_constraint(errors, columns, row_number):
    for column in columns:
        if len(column) == 4:
            valid = column['field'].test_value(column['value'], constraint='maximum')
            if not valid:
                # Add error
                message = spec['errors']['maximum-constraint']['message']
                message = message.format(
                    value=column['value'],
                    row_number=row_number,
                    column_number=column['number'],
                    constraint=column['field'].constraints['maximum'])
                errors.append({
                    'code': 'maximum-constraint',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })
