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

    def check_row(self, cells):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['column-number'], item['header']]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Sequential value check requires column "{column}" to exist'
            message = message.format(column=self.__column)
            error = Error(
                self.__code,
                row_number=cells[0]['row-number'],
                message=message
            )
            return [error]

        # Get value
        try:
            value = int(cell.get('value'))
        except (TypeError, ValueError):
            message = (
                'Sequential value check requires column "{column_number}"'
                ' to be an integer'
            )
            error = self._create_error(cell, message)
            return [error]

        # Initiate cursor
        if self.__cursor is None:
            self.__cursor = value

        # Check value
        if self.__cursor != value:
            self.__cursor = value + 1
            message = (
                'Value "{value}" is not a sequential in column {column_number}'
                ' for row {row_number}'
            )
            message_substitutions = {
                'value': value,
            }
            error = self._create_error(cell, message, message_substitutions)
            return [error]

        # Increment cursor
        self.__cursor += 1

    def _create_error(self, cell, message, message_substitutions=None):
        return Error(
            self.__code,
            cell,
            message=message,
            message_substitutions=message_substitutions
        )
