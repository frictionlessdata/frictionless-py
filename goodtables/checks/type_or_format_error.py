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

@check('type-or-format-error')
def type_or_format_error(cells):
    errors = []

    for cell in copy(cells):

        field = cell.get('field')
        value = cell.get('value')

        # Skip if cell has no field
        if field is None:
            continue

        # Cast value
        try:
            valid = True
            cell['value'] = field.cast_value(value, constraints=False)
        except tableschema.exceptions.TableSchemaException:
            valid = False

        # Skip if valid
        if valid:
            continue

        # Add error
        message_substitutions = {
            'value': '"{}"'.format(value),
            'field_type': '"{}"'.format(field.type),
            'field_format': '"{}"'.format(field.format),
        }
        error = Error(
            'type-or-format-error',
            cell,
            message_substitutions=message_substitutions
        )
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
