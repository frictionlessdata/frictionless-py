# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..registry import check


# Module API

@check('missing-value', type='structure', context='body')
def missing_value(errors, cells, row_number):
    for cell in copy(cells):

        # Skip if value in cell
        if 'value' in cell:
            continue

        # Add error
        message = spec['errors']['missing-value']['message']
        message = message.format(
            row_number=row_number,
            column_number=cell['number'])
        errors.append({
            'code': 'missing-value',
            'message': message,
            'row-number': row_number,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
