# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy


# Module API

def missing_header(columns, sample=None):
    errors = []
    for column in copy(columns):
        if 'header' not in column:
            columns.remove(column)
            errors.append({
                'message': 'Missing header',
                'row-number': None,
                'col-number': column['number'],
            })
    return errors
