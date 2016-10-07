# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json


# Module API

def duplicate_row(row_number, columns, state):
    errors = []
    rindex = state.setdefault('rindex', {})
    pointer = hash(json.dumps(list(column.get('value') for column in columns)))
    references = rindex.setdefault(pointer, [])
    if references:
        # Add error
        errors.append({
            'message': 'Duplicate row: %s' % references,
            'row-number': row_number,
            'column-number': None,
        })
        # Clear columns
        del columns[:]
    references.append(row_number)
    return errors
