# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import jsontableschema
from ..spec import spec
from ..decorators import check


# Module API

@check('non-castable-value')
def non_castable_value(errors, columns, row_number, state=None):
    for column in copy(columns):
        if len(column) == 4:
            try:
                column['value'] = column['field'].cast_value(
                    column['value'], skip_constraints=True)
            except jsontableschema.exceptions.JsonTableSchemaException:
                # Add error
                message = spec['errors']['non-castable-value']['message']
                message = message.format(
                    value=column['value'],
                    row_number=row_number,
                    column_number=column['number'],
                    field_type=column['field'].type,
                    field_format=column['field'].format)
                errors.append({
                    'code': 'non-castable-value',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })
                # Remove column
                columns.remove(column)
