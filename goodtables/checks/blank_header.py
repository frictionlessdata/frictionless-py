# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..spec import spec
from ..registry import check


# Module API

@check('blank-header', type='structure', context='head')
def blank_header(errors, cells, sample=None):
    for cell in cells:

        # Skip if cell have non blank header
        if cell.get('header', True):
            continue

        # Add error
        message = spec['errors']['blank-header']['message']
        message = message.format(column_number=cell['number'])
        errors.append({
            'code': 'blank-header',
            'message': message,
            'row-number': None,
            'column-number': cell['number'],
        })
