# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from jsontableschema import Schema, infer
from ..spec import spec
from ..decorators import check


# Module API

@check('extra-header')
def extra_header(errors, columns, sample, infer_fields=False):
    for column in copy(columns):
        if 'field' not in column:
            # Infer field
            if infer_fields:
                column_sample = []
                for row in sample:
                    value = None
                    if len(row) > column['number']:
                        value = row[column['number']]
                    column_sample.append(value)
                descriptor = infer([column['header']], column_sample)
                column['field'] = Schema(descriptor).fields[0]
            # Add error/remove column
            else:
                message = spec['errors']['extra-header']['message']
                message = message.format(column_number=column['number'])
                errors.append({
                    'code': 'extra-header',
                    'message': message,
                    'row-number': None,
                    'column-number': column['number'],
                })
                columns.remove(column)
