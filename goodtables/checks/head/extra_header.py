# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from jsontableschema import Schema, infer


# Module API

def extra_header(columns, sample, infer_fields=False):
    errors = []
    for column in copy(columns):
        if 'field' not in column:
            errors.append({
                'message': 'Extra header',
                'row-number': None,
                'col-number': column['number'],
            })
            if not infer_fields:
                columns.remove(column)
                continue
            column_sample = []
            for row in sample:
                value = None
                if len(row) > column['number']:
                    value = row[column['number']]
                column_sample.append(value)
            descriptor = infer([column['header']], column_sample)
            column['field'] = Schema(descriptor).fields[0]
    return errors
