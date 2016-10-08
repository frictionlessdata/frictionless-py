# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('blank-row')
def blank_row(row_number, columns, state=None):
    errors = []
    if not list(filter(lambda column: column.get('value'), columns)):
        # Add error
        errors.append({
            'message': 'Blank row',
            'row-number': row_number,
            'column-number': None,
        })
        # Clear columns
        del columns[:]
    return errors
