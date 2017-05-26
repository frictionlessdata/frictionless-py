# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..spec import spec
from ..decorators import check


# Module API

@check('missing-header')
def missing_header(errors, columns, sample=None):
    for column in copy(columns):
        if 'header' not in column:
            # Add error
            message = spec['errors']['missing-header']['message']
            message = message.format(column_number=column['number'])
            errors.append({
                'code': 'missing-header',
                'message': message,
                'row-number': None,
                'column-number': column['number'],
            })
            # Remove column
            columns.remove(column)
