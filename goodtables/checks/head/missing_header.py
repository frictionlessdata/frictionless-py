# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ...register import check


# Module API

@check('missing-header')
def missing_header(errors, columns, sample=None):
    for column in copy(columns):
        if 'header' not in column:
            # Add error
            errors.append({
                'code': 'missing-header',
                'message': 'Missing header',
                'row-number': None,
                'column-number': column['number'],
            })
            # Remove column
            columns.remove(column)
