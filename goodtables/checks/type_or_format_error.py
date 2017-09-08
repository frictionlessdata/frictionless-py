# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import tableschema
from ..spec import spec
from ..registry import check


# Module API

@check('type-or-format-error', type='schema', context='body')
def type_or_format_error(errors, cells, row_number):
    for cell in copy(cells):

        # Skip if cell is incomplete
        if not set(cell).issuperset(['number', 'header', 'field', 'value']):
            continue

        # Cast value
        try:
            valid = True
            cell['value'] = cell['field'].cast_value(cell['value'], constraints=False)
        except tableschema.exceptions.TableSchemaException:
            valid = False

        # Skip if valid
        if valid:
            continue

        # Add error
        message = spec['errors']['type-or-format-error']['message']
        message = message.format(
            value='"%s"' % cell['value'],
            row_number=row_number,
            column_number=cell['number'],
            field_type='"%s"' % cell['field'].type,
            field_format='"%s"' % cell['field'].format)
        errors.append({
            'code': 'type-or-format-error',
            'message': message,
            'row-number': row_number,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
