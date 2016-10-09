# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ...registry import check


# Module API

@check('extra-value')
def extra_value(errors, columns, row_number, state=None):
    for column in copy(columns):
        if 'header' not in column:
            # Add error
            errors.append({
                'code': 'extra-value',
                'message': 'Extra value',
                'row-number': row_number,
                'column-number': column['number'],
            })
            # Remove column
            columns.remove(column)
