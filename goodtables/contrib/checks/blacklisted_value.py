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

    def check_row(self, cells, row_number):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['number'], item.get('header')]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Blacklisted value check requires column "{column_number}" to exist'
            error = Error(
                'blacklisted-value',
                cell,
                row_number=row_number
            )
            return [error]

        # Check value
        value = cell.get('value')
        if value in self.__blacklist:
            message = 'Value "{value}" in column {column_number} for row {row_number} is blacklisted'
            message_substitutions = {
                'value': value,
            }
            error = Error(
                'blacklisted-value',
                cell,
                row_number,
                message,
                message_substitutions=message_substitutions
            )
            return [error]
