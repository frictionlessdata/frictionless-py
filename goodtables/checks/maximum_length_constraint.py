# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..decorators import check


# Module API

@check('maximum-length-constraint')
def maximum_length_constraint(errors, columns, row_number, state=None):
    for column in columns:
        if len(column) == 4:
            valid = column['field'].test_value(column['value'], constraint='maxLength')
            if not valid:
                # Add error
                message = spec['errors']['maximum-length-constraint']['message']
                message = message.format(
                    value=column['value'],
                    row_number=row_number,
                    column_number=column['number'],
                    constraint=column['field'].constraints['maxLength'])
                errors.append({
                    'code': 'maximum-length-constraint',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })
