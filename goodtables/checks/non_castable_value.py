# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import jsontableschema
from ..spec import spec
from ..registry import check


# Module API

@check('non-castable-value', type='schema', context='body')
def non_castable_value(errors, cells, row_number):
    for cell in copy(cells):

        # Skip if cell is incomplete
        if not set(cell).issuperset(['number', 'header', 'field', 'value']):
            continue

        # Cast value
        try:
            valid = True
            cell['value'] = cell['field'].cast_value(cell['value'], skip_constraints=True)
        except jsontableschema.exceptions.JsonTableSchemaException:
            valid = False

        # Skip if valid
        if valid:
            continue

        # Add error
        message = spec['errors']['non-castable-value']['message']
        message = message.format(
            value=cell['value'],
            row_number=row_number,
            column_number=cell['number'],
            field_type=cell['field'].type,
            field_format=cell['field'].format)
        errors.append({
            'code': 'non-castable-value',
            'message': message,
            'row-number': row_number,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
