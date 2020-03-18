# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('missing-header')
def missing_header(cells, sample):
    errors = []

    for cell in copy(cells):

        # Skip if header in cell
        if cell.get('header') is not None:
            continue

        # Add error
        field_name = cell['field'].name if cell['field'] else ''
        message_substitutions = {'field_name': '"{}"'.format(field_name)}
        message = 'There is a missing header in column {column_number}'
        # It's a temporary solution for
        # https://github.com/frictionlessdata/goodtables-py/issues/338
        if not cell.get('column-number'):
            message = 'There is a missing header in column {field_name}'
        error = Error(
            'missing-header',
            cell,
            message=message,
            message_substitutions=message_substitutions
        )
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
