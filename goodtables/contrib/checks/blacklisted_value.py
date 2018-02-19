# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check
from ...error import Error


# Module API

@check('blacklisted-value', type='custom', context='body')
class BlacklistedValue(object):

    # Public

    def __init__(self, column, blacklist, **options):
        self.__column = column
        self.__blacklist = blacklist

    def check_row(self, cells):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['column-number'], item['header']]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Blacklisted value check requires column "{column}" to exist'
            message = message.format(column=self.__column)
            error = Error(
                'blacklisted-value',
                row_number=cells[0]['row-number'],
                message=message
            )
            return [error]

        # Check value
        value = cell.get('value')
        if value in self.__blacklist:
            message = (
                'Value "{value}" in column {column_number} on row {row_number}'
                ' is blacklisted'
            )
            message_substitutions = {
                'value': value,
            }
            error = Error(
                'blacklisted-value',
                cell,
                message=message,
                message_substitutions=message_substitutions
            )
            return [error]
