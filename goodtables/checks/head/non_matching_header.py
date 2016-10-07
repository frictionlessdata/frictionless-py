# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy


# Module API

def non_matching_header(columns, sample=None, order_fields=False):
    errors = []
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
                     'message': 'Non matching header',
                     'row-number': None,
                     'col-number': column['number'],
                })
                columns.remove(column)
    return errors
