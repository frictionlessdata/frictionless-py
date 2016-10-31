# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from copy import copy
from ...register import check


# Module API

@check('non-matching-header')
def non_matching_header(errors, columns, sample=None, order_fields=False):

    # No field ordering
    if not order_fields:
        for column in copy(columns):
            if len(column) == 3:
                if column['header'] != column['field'].name:
                    # Add error
                    message = 'Header in column %s doesn\'t match field name (name: %s)'
                    message = message % (column['number'], column['field'].name)
                    errors.append({
                        'code': 'non-matching-header',
                        'message': message,
                        'row-number': None,
                        'column-number': column['number'],
                    })
                    if _slugify(column['header']) != _slugify(column['field'].name):
                        # Remove column
                        columns.remove(column)

    # Field ordering
    else:
        raise NotImplementedError()


# Internal

def _slugify(string):
    string = re.sub(r'[\W_]+', '', string)
    string = string.lower()
    return string
