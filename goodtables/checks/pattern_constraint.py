# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..decorators import check


# Module API

@check('pattern-constraint')
def pattern_constraint(errors, columns, row_number, state=None):
    for column in copy(columns):
        if len(column) == 4:
            valid = column['field'].test_value(column['value'], constraint='pattern')
            if not valid:
                # Add error
                message = spec['errors']['pattern-constraint']['message']
                message = message.format(
                    value=column['value'],
                    row_number=row_number,
                    column_number=column['number'],
                    constraint=column['field'].constraints['pattern'])
                errors.append({
                    'code': 'pattern-constraint',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })
                # Remove column
                columns.remove(column)
