# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('sequential-column', type='custom', context='body')
class SequentialColumn(object):

    # Public

    def __init__(self, column, **options):
        self.__column = column
        self.__cursor = None

    def check_row(self, errors, columns, row_number):

        # Get column
        column = None
        for item in columns:
            if self.__column in [item['number'], item['header']]:
                column = item
                break

        # Check column
        if not column:
            return errors.append({
                'code': 'sequential-column',
                'message': 'Sequential column violation',
                'row-number': row_number,
                'column-number': None,
            })

        # Get value
        try:
            value = int(column['value'])
        except ValueError:
            return errors.append({
                'code': 'sequential-column',
                'message': 'Sequential column violation',
                'row-number': row_number,
                'column-number': column['number'],
            })

        # Initiate cursor
        if self.__cursor is None:
            self.__cursor = value

        # Check value
        if self.__cursor != value:
            self.__cursor = value
            return errors.append({
                'code': 'sequential-column',
                'message': 'Sequential column violation',
                'row-number': row_number,
                'column-number': column['number'],
            })

        # Increment cursor
        self.__cursor += 1
