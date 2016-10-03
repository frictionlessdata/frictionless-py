# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def blank_row(cells, state=None):
    errors = []
    row_number = cells[0]['row-number']
    if not list(filter(lambda cell: cell['value'], cells)):
        cells.clear()
        errors.append({
            'message': 'Blank row',
            'row-number': row_number,
            'col-number': None,
        })
    return errors
