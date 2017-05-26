# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..decorators import check


# Module API

@check('missing-value')
def missing_value(errors, columns, row_number, state=None):
    for column in copy(columns):
        if 'value' not in column:
            # Add error
            message = spec['errors']['missing-value']['message']
            message = message.format(
                row_number=row_number,
                column_number=column['number'])
            errors.append({
                'code': 'missing-value',
                'message': message,
                'row-number': row_number,
                'column-number': column['number'],
            })
            # Remove column
            columns.remove(column)
