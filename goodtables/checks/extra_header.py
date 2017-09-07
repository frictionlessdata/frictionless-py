# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from tableschema import Schema
from ..spec import spec
from ..registry import check


# Module API

@check('extra-header', type='schema', context='head')
class ExtraHeader(object):

    # Public
    def __init__(self, infer_fields=False, **options):
        self.__infer_fields = infer_fields

    def check_headers(self, errors, cells, sample):
        for cell in copy(cells):

            # Skip if cell has field
            if 'field' in cell:
                continue

            # Infer field
            if self.__infer_fields:
                column_sample = []
                for row in sample:
                    value = None
                    if len(row) > cell['number']:
                        value = row[cell['number']]
                    column_sample.append(value)
                schema = Schema()
                schema.infer(column_sample, headers=[cell['header']])
                cell['field'] = schema.fields[0]

            # Add error/remove column
            else:
                message = spec['errors']['extra-header']['message']
                message = message.format(column_number=cell['number'])
                errors.append({
                    'code': 'extra-header',
                    'message': message,
                    'row-number': None,
                    'column-number': cell['number'],
                })
                cells.remove(cell)
