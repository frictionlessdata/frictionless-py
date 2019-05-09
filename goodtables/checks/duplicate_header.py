# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('duplicate-header')
def duplicate_header(cells, sample=None):
    errors = []

    rindex = {}
    cell_by_column_number = {}
    for cell in cells:

        # Skip if not header
        if 'header' not in cell:
            continue

        header_indexes = rindex.get(cell['header'], set())
        header_indexes.add(cell['column-number'])

        rindex[cell['header']] = header_indexes
        cell_by_column_number[cell['column-number']] = cell

    for header_value, header_indexes in rindex.items():
        if len(header_indexes) == 1:
            continue

        header_indexes_list = sorted(header_indexes)
        first_header_index, other_header_indexes = header_indexes_list[0], header_indexes_list[1:]  # noqa
        for other_header_index in other_header_indexes:
            duplicates = header_indexes - {other_header_index}
            message_substitutions = {
                'original': str(first_header_index),
                'column_numbers': ', '.join(map(str, duplicates)),
            }
            cell = cell_by_column_number[other_header_index]
            error = Error(
                'duplicate-header',
                cell,
                message_substitutions=message_substitutions
            )
            errors.append(error)

    return errors
