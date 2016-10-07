# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import tabulator


# Module API

def io_error(exception):
    errors = []
    if isinstance(exception, tabulator.exceptions.TabulatorException):
        # Add erorr
        errors.append({
            'message': 'IO error',
            'row-number': None,
            'column-number': None,
        })
    return errors
