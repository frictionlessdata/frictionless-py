# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import datapackage


# Module API

def datapackage_error(exception):
    errors = []
    if isinstance(exception, datapackage.exceptions.ValidationError):
        # Add error
        errors.append({
            'message': 'Datapackage validation error',
            'row-number': None,
            'column-number': None,
        })
    return errors
