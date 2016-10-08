# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import tabulator
from ...registry import check


# Module API

@check('scheme-error')
def scheme_error(exception):
    errors = []
    if isinstance(exception, tabulator.exceptions.TabulatorException):
        # Add error
        errors.append({
            'message': 'Scheme error',
            'row-number': None,
            'column-number': None,
        })
    return errors
