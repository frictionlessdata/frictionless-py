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
    for cell in cells:

        # Skip if not header
        if 'header' not in cell:
            continue

        header_indexes = rindex.get(cell['header'], set())
        header_indexes.add(cell['column-number'])

        rindex[cell['header']] = header_indexes

    for header_value, header_indexes in rindex.items():
        if len(header_indexes) == 1:
            continue

        for header_index in sorted(header_indexes)[1:]:
            duplicates = header_indexes - {header_index}
            message_substitutions = {
                'column_numbers': ', '.join(map(str, duplicates)),
            }
            error = Error(
                'duplicate-header',
                cell,
                message_substitutions=message_substitutions
            )
            errors.append(error)

    return errors
