# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def blank_row(row_number, columns, state=None):
    errors = []
    if not list(filter(lambda column: column['value'], columns)):
        del columns[:]
        errors.append({
            'message': 'Blank row',
            'row-number': row_number,
            'col-number': None,
        })
    return errors
