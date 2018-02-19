# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('unique-constraint')
class UniqueConstraint(object):

    # Public

    def __init__(self, **options):
        self.__unique_fields_cache = None

    def check_row(self, cells):
        errors = []

        # Prepare unique checks
        if self.__unique_fields_cache is None:
            self.__unique_fields_cache = _create_unique_fields_cache(cells)

        # Check unique
        for column_numbers, cache in self.__unique_fields_cache.items():
            column_cells = tuple(
                cell
                for column_number, cell in enumerate(cells, start=1)
                if column_number in column_numbers
            )
            column_values = tuple(cell.get('value') for cell in column_cells)
            row_number = column_cells[0]['row-number']

            all_values_are_none = (set(column_values) == {None})
            if not all_values_are_none:
                if column_values in cache['data']:
                    message_substitutions = {
                        'row_numbers': ', '.join(map(str, cache['refs'] + [row_number])),
                    }

                    # FIXME: The unique constraint can be related to multiple
                    # columns (e.g. a composite primary key), but here we only
                    # pass the 1st column.
                    error = Error(
                        'unique-constraint',
                        column_cells[0],
                        message_substitutions=message_substitutions
                    )
                    errors.append(error)
                cache['data'].add(column_values)
                cache['refs'].append(row_number)

        return errors

# Internal


def _create_unique_fields_cache(cells):
    primary_key_column_numbers = []
    cache = {}

    # Unique
    for column_number, cell in enumerate(cells, start=1):
        field = cell.get('field')
        if field is not None:
            if field.descriptor.get('primaryKey'):
                primary_key_column_numbers.append(column_number)
            if field.constraints.get('unique'):
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
