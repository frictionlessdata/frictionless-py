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
        self.__row_indexes = {}

    def check_row(self, errors, cells, row_number):
        for cell in cells:

            # Skip if cell is incomplete
            if not set(cell).issuperset(['number', 'header', 'field', 'value']):
                continue

            # Skip if not constraint
            constraint = cell['field'].constraints.get('unique')
            if not constraint:
                continue

            # Get references
            rindex = self.__row_indexes.setdefault(cell['number'], {})
            references = rindex.setdefault(cell['value'], [])

            # Add error
            if references:
                message = spec['errors']['unique-constraint']['message']
                message = message.format(
                    row_numbers=', '.join(map(str, references + [row_number])),
                    column_number=cell['number'])
                errors.append({
                    'code': 'unique-constraint',
                    'message': message,
                    'row-number': row_number,
                    'column-number': cell['number'],
                })

            # Update references
            references.append(row_number)
