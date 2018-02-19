# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import statistics
from ...registry import check
from ...error import Error
from ... import exceptions


# Module API

@check('deviated-value', type='custom', context='body')
class DeviatedValue(object):

    # Public

    def __init__(self, column, average='mean', interval=3, **options):

        # Set attributes
        self.__column = column
        self.__interval = interval
        self.__column_cells = []
        self.__average_function = _AVERAGE_FUNCTIONS.get(average)
        self.__code = 'deviated-value'
        self.__cell = None

        # Validate average
        if not self.__average_function:
            message = 'Deviated value check supports only this average functions: %s'
            message = message % ', '.join(_AVERAGE_FUNCTIONS.keys())
            raise exceptions.GoodtablesError(message)

    def check_row(self, cells):

        # Get cell
        for cell in cells:
            if self.__column in [cell['column-number'], cell['header']]:
                self.__cell = cell
                break

        # Check cell
        if not self.__cell:
            message = 'Deviated value check requires column "{column}" to exist'
            message = message.format(column=self.__column)
            error = Error(
                self.__code,
                row_number=cells[0]['row-number'],
                message=message
            )
            return [error]

        # Get value
        try:
            float(cell['value'])
        except ValueError:
            message = (
                'Deviated value check requires column "{column_number}"'
                ' to be a number'
            )
            error = Error(
                self.__code,
                self.__cell,
                message=message
            )
            return [error]

        # Collect value
        self.__column_cells.append(cell)

    def check_table(self):

        # Skip if not values
        if not self.__column_cells or len(self.__column_cells) < 2:
            return

        # Prepare interval
        try:
            values = [float(cell['value']) for cell in self.__column_cells]
            stdev = statistics.stdev(values)
            average = self.__average_function(values)
            minimum = average - stdev * self.__interval
            maximum = average + stdev * self.__interval
        except Exception as exception:
            message = 'Deviated value check calculation issue: %s' % exception
            error = Error(
                self.__code,
                self.__cell,
                message=message
            )
            return [error]

        # Check values
        errors = []
        for cell in self.__column_cells:
            if not (minimum <= float(cell['value']) <= maximum):
                message = (
                    'Deviated value "{value}" in column {column_number}'
                    ' for row {row_number}'
                )
                message_substitutions = {
                    'value': cell['value'],
                }
                error = Error(
                    self.__code,
                    cell,
                    message=message,
                    message_substitutions=message_substitutions
                )
                errors.append(error)

        return errors


# Internal

_AVERAGE_FUNCTIONS = {
    'mean': statistics.mean,
    'median': statistics.median,
    'mode': statistics.mode,
}
