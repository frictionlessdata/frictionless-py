# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json


# Module API

def duplicate_row(cells, state):
    errors = []
    row_number = cells[0]['row-number']
    revert_index = state.setdefault('revert_index', {})
    pointer = hash(json.dumps(list(cell['value'] for cell in cells)))
    references = revert_index.setdefault(pointer, [])
    if references:
        cells.clear()
        errors.append({
            'message': 'Duplicate row: %s' % references,
            'row-number': row_number,
            'col-number': None,
        })
    references.append(row_number)
    return errors
