# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from ...register import check


# Module API

@check('duplicate-row')
def duplicate_row(errors, columns, row_number, state):
    rindex = state.setdefault('rindex', {})
    pointer = hash(json.dumps(list(column.get('value') for column in columns)))
    references = rindex.setdefault(pointer, [])
    if references:
        # Add error
        message = 'Row %s is duplicated to row(s) %s'
        message = message % (row_number, ', '.join(map(str, references)))
        errors.append({
            'code': 'duplicate-row',
            'message': message,
            'row-number': row_number,
            'column-number': None,
        })
        # Clear columns
        del columns[:]
    references.append(row_number)
