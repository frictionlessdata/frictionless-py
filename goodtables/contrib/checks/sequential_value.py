# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('sequential-value', type='custom', context='body')
class SequentialValue(object):

    # Public

    def __init__(self, column, **options):
        self.__column = column
        self.__cursor = None

    def check_row(self, errors, cells, row_number):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['number'], item.get('header')]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Sequential value check requires column "%s" to exist'
            return errors.append({
                'code': 'sequential-value',
                'message': message % self.__column,
                'row-number': row_number,
                'column-number': None,
            })

        # Get value
        try:
            value = int(cell.get('value'))
        except (TypeError, ValueError):
            message = 'Sequential value check requires column "%s" to be an integer'
            return errors.append({
                'code': 'sequential-value',
                'message': message % self.__column,
                'row-number': row_number,
                'column-number': cell['number'],
            })

        # Initiate cursor
        if self.__cursor is None:
            self.__cursor = value

        # Check value
        if self.__cursor != value:
            self.__cursor = value + 1
            message = 'Value "%s" is not a sequential in column %s for row %s'
            return errors.append({
                'code': 'sequential-value',
                'message': message % (value, cell['number'], row_number),
                'row-number': row_number,
                'column-number': cell['number'],
            })

        # Increment cursor
        self.__cursor += 1
