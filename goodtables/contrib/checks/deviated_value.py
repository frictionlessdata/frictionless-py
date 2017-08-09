# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import statistics
from collections import OrderedDict
from ...registry import check
from ... import exceptions


# Module API

@check('deviated-value', type='custom', context='body')
class DeviatedValue(object):

    # Public

    def __init__(self, column, average='mean', interval=3, **options):

        # Set attributes
        self.__column = column
        self.__interval = interval
        self.__column_number = None
        self.__column_values = OrderedDict()
        self.__average_function = _AVERAGE_FUNCTIONS.get(average)

        # Validate average
        if not self.__average_function:
            message = 'Deviated value check supports only this average functions: %s'
            message = message % ', '.join(_AVERAGE_FUNCTIONS.keys())
            raise exceptions.GoodtablesError(message)

    def check_row(self, errors, cells, row_number):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['number'], item.get('header')]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Deviated value check requires column "%s" to exist'
            return errors.append({
                'code': 'deviated-value',
                'message': message % self.__column,
                'row-number': row_number,
                'column-number': None,
            })

        # Get value
        try:
            value = float(cell['value'])
        except ValueError:
            message = 'Deviated value check requires column "%s" to be a number'
            return errors.append({
                'code': 'deviated-value',
                'message': message % self.__column,
                'row-number': row_number,
                'column-number': cell['number'],
            })

        # Collect value
        self.__column_values[row_number] = value
        self.__column_number = cell['number']

    def check_table(self, errors):

        # Skip if not values
        if not self.__column_values:
            return

        # Prepare interval
        try:
            stdev = statistics.stdev(self.__column_values.values())
            average = self.__average_function(self.__column_values.values())
            minimum = average - stdev * self.__interval
            maximum = average + stdev * self.__interval
        except Exception as exception:
            message = 'Deviated value check calculation issue: %s' % exception
            return errors.append({
                'code': 'deviated-value',
                'message': message,
                'row-number': None,
                'column-number': self.__column_number,
            })

        # Check values
        for row_number, value in self.__column_values.items():
            if not (minimum <= value <= maximum):
                message = 'Deviated value "%s" in column %s for row %s'
                errors.append({
                    'code': 'deviated-value',
                    'message': message % (value, self.__column_number, row_number),
                    'row-number': row_number,
                    'column-number': self.__column_number,
                })


# Internal

_AVERAGE_FUNCTIONS = {
    'mean': statistics.mean,
    'median': statistics.median,
    'mode': statistics.mode,
}
