# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import jsontableschema


# Module API

def bad_value(row_number, columns, state=None):
    errors = []
    for column in copy(columns):
        try:
            column['value'] = column['field'].cast_value(column['value'])
        except jsontableschema.exceptions.JsonTableSchemaException:
            columns.remove(column)
            errors.append({
                'message': 'Bad value',
                'row-number': row_number,
                'col-number': column['number'],
            })
    return errors
