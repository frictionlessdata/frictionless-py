# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import copy
from ..registry import check
from ..error import Error


# Module API

@check('missing-header')
def missing_header(cells, sample):
    errors = []

    for cell in copy(cells):

        # Skip if header in cell
        if cell.get('header') is not None:
            continue

        # Add error
        message_substitutions = {
            'field_name': '"{}"'.format(cell['field'].name),
        }
        error = Error(
            'missing-header',
            cell,
            message_substitutions=message_substitutions
        )
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors
