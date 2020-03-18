# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict

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
                for _, cell in enumerate(cells, start=1)
                if cell["column-number"] in column_numbers
            )
            if column_cells:
                column_values = tuple(cell.get('value') for cell in column_cells)
                row_number = column_cells[0]['row-number']

                all_values_are_none = (set(column_values) == {None})
                if not all_values_are_none:
                    if len(cache[column_values]) > 0:
                        if len(cache[column_values]) <= 5:
                            message_substitutions = {
                                "row_numbers": ", ".join(
                                    map(str, cache[column_values] + [row_number])
                                ),
                            }
                        else:
                            message_substitutions = {
                                "row_numbers": "{rows} and {count} others".format(
                                    rows=", ".join(map(str, cache[column_values][:3] + [row_number])),
                                    count=len(cache[column_values]) - 4
                                )
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
                    cache[column_values].append(row_number)

        return errors

# Internal


def _create_unique_fields_cache(cells):
    primary_key_column_numbers = []
    cache = {}

    # Unique
    for _, cell in enumerate(cells, start=1):
        field = cell.get('field')
        column_number = cell.get('column-number')
        if field is not None:
            if field.descriptor.get('primaryKey'):
                primary_key_column_numbers.append(column_number)
            if field.constraints.get('unique'):
                cache[tuple([column_number])] = defaultdict(list)

    # Primary key
    if primary_key_column_numbers:
        cache[tuple(primary_key_column_numbers)] = defaultdict(list)

    return cache
