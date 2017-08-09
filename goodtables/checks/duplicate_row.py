# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from ..spec import spec
from ..registry import check


# Module API

@check('duplicate-row', type='structure', context='body')
class DuplicateRow(object):

    # Public

    def __init__(self, **options):
        self.__row_index = {}

    def check_row(self, errors, cells, row_number):

        # Get pointer
        try:
            pointer = hash(json.dumps(list(cell.get('value') for cell in cells)))
            references = self.__row_index.setdefault(pointer, [])
        except TypeError:
            pointer = None

        # Found pointer
        if pointer:

            # Add error
            if references:
                message = spec['errors']['duplicate-row']['message']
                message = message.format(
                    row_number=row_number,
                    row_numbers=', '.join(map(str, references)))
                errors.append({
                    'code': 'duplicate-row',
                    'message': message,
                    'row-number': row_number,
                    'column-number': None,
                })

            # Clear cells
            if references:
                del cells[:]

            # Update references
            references.append(row_number)
