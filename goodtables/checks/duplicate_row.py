# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from ..registry import check
from ..error import Error


# Module API

@check('duplicate-row')
class DuplicateRow(object):

    # Public

    def __init__(self, **options):
        self.__row_index = {}

    def check_row(self, cells):
        errors = []

        # Get pointer
        try:
            pointer = hash(json.dumps(list(cell.get('value') for cell in cells)))
            references = self.__row_index.setdefault(pointer, [])
        except TypeError:
            pointer = None

        # Found pointer
        if pointer:

            row_number = cells[0].get('row-number')

            # Add error
            if references:
                message_substitutions = {
                    'row_numbers': ', '.join(map(str, references)),
                }
                error = Error(
                    'duplicate-row',
                    row_number=row_number,
                    message_substitutions=message_substitutions
                )
                errors.append(error)

            # Clear cells
            if references:
                del cells[:]

            # Update references
            references.append(row_number)

        return errors
