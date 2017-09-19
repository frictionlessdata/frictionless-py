# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('unique-constraint', type='schema', context='body')
class UniqueConstraint(object):

    # Public

    def __init__(self, **options):
        self.__unique_fields_cache = None

    def check_row(self, errors, cells, row_number):

        # Prepare unique checks
        if self.__unique_fields_cache is None:
            self.__unique_fields_cache = _create_unique_fields_cache(cells)

        # Check unique
        for column_numbers, cache in self.__unique_fields_cache.items():
            values = tuple(cell.get('value')
                for column_number, cell in enumerate(cells, start=1)
                if column_number in column_numbers)
            if not all(map(lambda value: value is None, values)):
                if values in cache['data']:
                    message = spec['errors']['unique-constraint']['message']
                    message = message.format(
                        row_numbers=', '.join(map(str, cache['refs'] + [row_number])),
                        column_number=', '.join(map(str, column_numbers)))
                    errors.append({
                        'code': 'unique-constraint',
                        'message': message,
                        'row-number': row_number,
                        'column-number': column_numbers[0],
                    })
                cache['data'].add(values)
                cache['refs'].append(row_number)


# Internal

def _create_unique_fields_cache(cells):
    primary_key_column_numbers = []
    cache = {}

    # Unique
    for column_number, cell in enumerate(cells, start=1):
        if 'field' in cell:
            if cell['field'].descriptor.get('primaryKey'):
                primary_key_column_numbers.append(column_number)
            if cell['field'].constraints.get('unique'):
                cache[tuple([column_number])] = {
                    'data': set(),
                    'refs': [],
                }

    # Primary key
    if primary_key_column_numbers:
        cache[tuple(primary_key_column_numbers)] = {
            'data': set(),
            'refs': [],
        }

    return cache
