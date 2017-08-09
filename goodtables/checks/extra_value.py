# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..registry import check


# Module API

@check('extra-value', type='structure', context='body')
def extra_value(errors, cells, row_number):
    for cell in copy(cells):

        # Skip if header in cell
        if 'header' in cell:
            continue

        # Add error
        message = spec['errors']['extra-value']['message']
        message = message.format(
            row_number=row_number,
            column_number=cell['number'])
        errors.append({
            'code': 'extra-value',
            'message': message,
            'row-number': row_number,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
