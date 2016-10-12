# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...register import check


# Module API

@check('blank-header')
def blank_header(errors, columns, sample=None):
    for column in columns:
        if 'header' in column:
            if not column['header']:
                # Add error
                message = 'Header in column %s is completely blank' % column['number']
                errors.append({
                    'code': 'blank-header',
                    'message': message,
                    'row-number': None,
                    'column-number': column['number'],
                })
