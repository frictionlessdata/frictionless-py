# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def duplicate_header(columns, sample=None):
    errors = []
    headers = set()
    for column in columns:
        if column['header'] in headers:
            # Add error
            errors.append({
                'message': 'Duplicate header',
                'row-number': None,
                'col-number': column['number'],
            })
            continue
        headers.add(column['header'])
    return errors
