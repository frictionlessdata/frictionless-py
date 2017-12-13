# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..error import Error


def create_check_constraint(check, constraint):
    def _check_constraint(cells, row_number):
        errors = []

        for cell in cells:

            # Skip if cell is incomplete
            if not set(cell).issuperset(['number', 'header', 'field', 'value']):
                continue

            # Check constraint
            valid = cell['field'].test_value(cell['value'], constraints=[constraint])

            # Add error
            if not valid:
                message_substitutions = {
                    'value': '"{}"'.format(cell['value']),
                    'constraint': '"{}"'.format(cell['field'].constraints[constraint]),
                }

                error = Error(
                    check,
                    cell,
                    row_number=row_number,
                    message_substitutions=message_substitutions
                )
                errors.append(error)

        return errors

    return _check_constraint
