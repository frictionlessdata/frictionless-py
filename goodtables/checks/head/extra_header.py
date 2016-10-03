# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Schema, infer


# Module API

def extra_header(columns, sample):
    errors = []
    for column in columns:
        if 'field' not in column:
            column_sample = []
            for row in sample:
                value = None
                if len(row) > column['number']:
                    value = row[column['number']]
                column_sample.append(value)
            column['field'] = Schema(infer([column['header']], column_sample)).fields[0]
            errors.append({
                'message': 'Extra header',
                'row-number': None,
                'col-number': column['number'],
            })
    return errors
