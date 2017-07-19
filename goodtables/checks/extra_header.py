# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from jsontableschema import Schema, infer
from ..spec import spec
from ..registry import check


# Module API

@check('extra-header', type='schema', context='head')
class ExtraHeader(object):

    # Public
    def __init__(self, infer_fields=False, **options):
        self.__infer_fields = infer_fields

    def check_headers(self, errors, columns, sample):
        for column in copy(columns):
            if 'field' not in column:
                # Infer field
                if self.__infer_fields:
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
