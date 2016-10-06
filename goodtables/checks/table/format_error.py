# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import tabulator


# Module API

def format_error(exception):
    errors = []
    if isinstance(exception, tabulator.exceptions.TabulatorException):
        # Add error
        errors.append({
            'message': 'Format error',
            'row-number': None,
            'col-number': None,
        })
    return errors
