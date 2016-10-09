# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ...registry import check


# Module API

@check('non-matching-header')
def non_matching_header(errors, columns, sample=None, order_fields=False):
    headers = set(column['name'] for column in columns if 'name' in column)
    field_names = set(column['field'].name for column in columns if 'field' in column)
    for column in copy(columns):
        header = column.get('header')
        field_name = None
        if 'field' in column:
            field_name = column['field'].name
        if header != field_name:
            if header in field_names or field_name in headers:
                errors.append({
                    'code': 'non-matching-header',
                    'message': 'Non matching header',
                    'row-number': None,
                    'column-number': column['number'],
                })
                columns.remove(column)
