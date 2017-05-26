# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..decorators import check


# Module API

@check('duplicate-header')
def duplicate_header(errors, columns, sample=None):
    rindex = {}
    for column in columns:
        if 'header' in column:
            references = rindex.setdefault(column['header'], [])
            if references:
                # Add error
                message = spec['errors']['duplicate-header']['message']
                message = message.format(
                    column_number=column['number'],
                    column_numbers=', '.join(map(str, references)))
                errors.append({
                    'code': 'duplicate-header',
                    'message': message,
                    'row-number': None,
                    'column-number': column['number'],
                })
            references.append(column['number'])
