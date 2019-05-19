# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from tableschema import Schema
from ..registry import check
from ..error import Error


# Module API

@check('extra-header')
class ExtraHeader(object):

    # Public
    def __init__(self, infer_fields=False, **options):
        self.__infer_fields = infer_fields

    def check_headers(self, cells, sample):
        errors = []

        for cell in copy(cells):

            # Skip if cell has field
            if 'field' in cell and cell['field'] is not None:
                continue

            # Infer field
            if self.__infer_fields:
                column_sample = []
                for row in sample:
                    value = None
                    if len(row) >= cell['column-number']:
                        value = row[cell['column-number'] - 1]
                    column_sample.append([value])
                schema = Schema()
                schema.infer(column_sample, headers=[cell.get('header')])
                cell['field'] = schema.fields[0]

            # Add error/remove column
            else:
                message_substitutions = {
                    'header': '"{}"'.format(cell.get('header')),
                }
                error = Error(
                    'extra-header',
                    cell,
                    message_substitutions=message_substitutions
                )
                errors.append(error)
                cells.remove(cell)

        return errors
