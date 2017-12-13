# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check
from ...error import Error


# Module API

@check('sequential-value', type='custom', context='body')
class SequentialValue(object):

    # Public

    def __init__(self, column, **options):
        self.__column = column
        self.__cursor = None
        self.__code = 'sequential-value'

    def check_row(self, cells, row_number):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['number'], item.get('header')]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Sequential value check requires column "{column_number}" to exist'
            error = self._create_error(cell, row_number, message)
            return [error]

        # Get value
        try:
            value = int(cell.get('value'))
        except (TypeError, ValueError):
            message = 'Sequential value check requires column "{column_number}" to be an integer'
            error = self._create_error(cell, row_number, message)
            return [error]

        # Initiate cursor
        if self.__cursor is None:
            self.__cursor = value

        # Check value
        if self.__cursor != value:
            self.__cursor = value + 1
            message = 'Value "{value}" is not a sequential in column {column_number} for row {row_number}'
            message_substitutions = {
                'value': value,
            }
            error = self._create_error(cell, row_number, message, message_substitutions)
            return [error]

        # Increment cursor
        self.__cursor += 1


    def _create_error(self, cell, row_number, message, message_substitutions=None):
        return Error(
            self.__code,
            cell,
            row_number=row_number,
            message=message,
            message_substitutions=message_substitutions
        )
