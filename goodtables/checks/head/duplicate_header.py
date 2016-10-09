# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('duplicate-header')
def duplicate_header(errors, columns, sample=None):
    headers = set()
    for column in columns:
        if 'header' in column:
            if column['header'] in headers:
                # Add error
                errors.append({
                    'code': 'duplicate-header',
                    'message': 'Duplicate header',
                    'row-number': None,
                    'column-number': column['number'],
                })
                continue
            headers.add(column['header'])
