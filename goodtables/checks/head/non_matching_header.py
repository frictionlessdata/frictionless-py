# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ...registry import check


# Module API

@check('non-matching-header')
def non_matching_header(errors, columns, sample=None, order_fields=False):

    # No field ordering
    if not order_fields:
        for column in copy(columns):
            if len(column) == 3:
                if column['header'] != column['field'].name:
                    # Add error
                    errors.append({
                        'code': 'non-matching-header',
                        'message': 'Non matching header',
                        'row-number': None,
                        'column-number': column['number'],
                    })
                    # Remove column
                    columns.remove(column)

    # Field ordering
    else:
        raise NotImplementedError()
