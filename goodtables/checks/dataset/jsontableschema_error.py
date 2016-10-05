# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import jsontableschema


# Module API

def jsontableschema_error(exception):
    errors = []
    if isinstance(exception, jsontableschema.exceptions.InvalidSchemaError):
        errors.append({
            'message': 'JSON Table Schema validation error',
            'row-number': None,
            'col-number': None,
        })
    return errors
