# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ...registry import check


# Module API

@check('blacklisted-value', type='custom', context='body')
class BlacklistedValue(object):

    # Public

    def __init__(self, column, blacklist, **options):
        self.__column = column
        self.__blacklist = blacklist

    def check_row(self, errors, cells, row_number):

        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['number'], item.get('header')]:
                cell = item
                break

        # Check cell
        if not cell:
            message = 'Blacklisted value check requires column "%s" to exist'
            return errors.append({
                'code': 'blacklisted-value',
                'message': message % self.__column,
                'row-number': row_number,
                'column-number': None,
            })

        # Check value
        value = cell.get('value')
        if value in self.__blacklist:
            message = 'Value "%s" in column %s for row %s is blacklisted'
            return errors.append({
                'code': 'blacklisted-value',
                'message': message % (value, cell['number'], row_number),
                'row-number': row_number,
                'column-number': cell['number'],
            })
