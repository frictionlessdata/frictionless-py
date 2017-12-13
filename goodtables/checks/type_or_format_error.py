# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import tableschema
from ..registry import check
from ..error import Error


# Module API

@check('type-or-format-error', type='schema', context='body')
def type_or_format_error(cells, row_number):
    errors = []

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
        message_substitutions = {
            'value': '"{}"'.format(cell['value']),
            'field_type': '"{}"'.format(cell['field'].type),
            'field_format': '"{}"'.format(cell['field'].format),
        }
        error = Error(
            'type-or-format-error',
            cell,
            row_number,
            message_substitutions=message_substitutions
        )
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
