# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy


# Module API

def missing_value(row_number, columns, state=None):
    errors = []
    for column in copy(columns):
        if 'value' not in column:
            # Add error
            errors.append({
                'message': 'Missing value',
                'row-number': row_number,
                'column-number': column['number'],
            })
            # Remove column
            columns.remove(column)
    return errors
