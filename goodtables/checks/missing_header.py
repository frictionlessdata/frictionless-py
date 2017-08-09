# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..registry import check


# Module API

@check('missing-header', type='schema', context='head')
def missing_header(errors, cells, sample=None):
    for cell in copy(cells):

        # Skip if header in cell
        if 'header' in cell:
            continue

        # Add error
        message = spec['errors']['missing-header']['message']
        message = message.format(column_number=cell['number'])
        errors.append({
            'code': 'missing-header',
            'message': message,
            'row-number': None,
            'column-number': cell['number'],
        })

        # Remove cell
        cells.remove(cell)
