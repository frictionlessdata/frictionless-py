# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy


# Module API

def extra_value(cells, state=None):
    errors = []
    for cell in copy(cells):
        if 'header' not in cell:
            cells.remove(cell)
            errors.append({
                'message': 'Extra value',
                'row-number': cell['row-number'],
                'col-number': cell['col-number'],
            })
    return errors
