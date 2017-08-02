# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('blank-row', type='structure', context='body')
def blank_row(errors, cells, row_number):
    if not list(filter(lambda cell: cell.get('value'), cells)):

        # Add error
        message = spec['errors']['blank-row']['message']
        message = message.format(row_number=row_number)
        errors.append({
            'code': 'blank-row',
            'message': message,
            'row-number': row_number,
            'column-number': None,
        })

        # Clear cells
        del cells[:]
