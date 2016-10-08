# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('blank-header')
def blank_header(columns, sample=None):
    errors = []
    for column in columns:
        if 'header' in column:
            if not column['header']:
                # Add error
                errors.append({
                    'message': 'Blank header',
                    'row-number': None,
                    'column-number': column['number'],
                })
    return errors
