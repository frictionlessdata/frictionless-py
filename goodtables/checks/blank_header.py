# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from ..error import Error


# Module API

@check('blank-header')
def blank_header(cells, sample=None):
    errors = []

    for cell in cells:

        # Skip if cell have non blank header
        if cell.get('header', False) or cell.get('is-virtual'):
            continue

        # Add error
        error = Error('blank-header', cell)
        errors.append(error)

    return errors
