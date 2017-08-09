# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('duplicate-header', type='structure', context='head')
def duplicate_header(errors, cells, sample=None):
    rindex = {}
    for cell in cells:

        # Skip if not header
        if 'header' not in cell:
            continue

        # Get references
        references = rindex.setdefault(cell['header'], [])

        # Add error
        if references:
            message = spec['errors']['duplicate-header']['message']
            message = message.format(
                column_number=cell['number'],
                column_numbers=', '.join(map(str, references)))
            errors.append({
                'code': 'duplicate-header',
                'message': message,
                'row-number': None,
                'column-number': cell['number'],
            })

        # Update references
        references.append(cell['number'])
