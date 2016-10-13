# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...register import check


# Module API

@check('duplicate-header')
def duplicate_header(errors, columns, sample=None):
    rindex = {}
    for column in columns:
        if 'header' in column:
            references = rindex.setdefault(column['header'], [])
            if references:
                # Add error
                message = 'Header in column %s is duplicated to header in column(s) %s'
                message = message % (column['number'], ', '.join(map(str, references)))
                errors.append({
                    'code': 'duplicate-header',
                    'message': message,
                    'row-number': None,
                    'column-number': column['number'],
                })
            references.append(column['number'])
