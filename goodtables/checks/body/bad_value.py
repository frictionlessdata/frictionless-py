# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
import jsontableschema


# Module API

def bad_value(cells, state=None):
    errors = []
    for cell in copy(cells):
        try:
            cell['value'] = cell['field'].cast_value(cell['value'])
        except jsontableschema.exceptions.JsonTableSchemaException:
            cells.remove(cell)
            errors.append({
                'message': 'Bad value',
                'row-number': cell['row-number'],
                'col-number': cell['col-number'],
            })
    return errors
