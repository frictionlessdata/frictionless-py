# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from ...registry import check
from ...error import Error


# Module API

@check('truncated-value', type='custom', context='body')
class TruncatedValue(object):

    # Public

    def __init__(self, **options):
        pass

    def check_row(self, cells):
        for cell in cells:
            value = cell.get('value')
            truncated = False

            # Skip no value
            if not value:
                continue

            # Check string cutoff
            if isinstance(value, six.string_types):
                if len(value) in _TRUNCATED_STRING_LENGTHS:
                    truncated = True

            # Check integer cutoff
            try:
                value = int(value)
                if value in _TRUNCATED_INTEGER_VALUES:
                    truncated = True
            except Exception:
                pass

            # Add error
            if truncated:
                message = (
                    'Value in column {column_number} for row {row_number}'
                    ' is probably truncated'
                )
                error = Error(
                    'truncated-value',
                    cell,
                    message=message
                )
                return [error]


# Internal

_TRUNCATED_STRING_LENGTHS = [
    255,
]
_TRUNCATED_INTEGER_VALUES = [
    # BigInt
    18446744073709551616,
    9223372036854775807,
    # Int
    4294967295,
    2147483647,
    # SummedInt
    2097152,
    # SmallInt
    65535,
    32767,
]
