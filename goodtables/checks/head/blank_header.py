# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def blank_header(columns, sample=None):
    errors = []
    for column in columns:
        if not column['header']:
            # Add error
            errors.append({
                'message': 'Blank header',
                'row-number': None,
                'column-number': column['number'],
            })
    return errors
