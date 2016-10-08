# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import jsontableschema
from ...registry import check


# Module API

@check('non-castable-value')
def non_castable_value(row_number, columns, state=None):
    errors = []
    for column in copy(columns):
        if len(column) == 4:
            try:
                column['value'] = column['field'].cast_value(column['value'])
            except jsontableschema.exceptions.JsonTableSchemaException:
                # Add error
                errors.append({
                    'message': 'Non castable value',
                    'row-number': row_number,
                    'column-number': column['number'],
                })
                # Remove column
                columns.remove(column)
    return errors
