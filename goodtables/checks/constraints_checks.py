# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..error import Error


def create_check_constraint(check, constraint):
    def _check_constraint(cells):
        errors = []

        for cell in cells:

            field = cell.get('field')
            value = cell.get('value')

            # Skip if cell has no field
            if field is None:
                continue

            # Check constraint
            valid = field.test_value(value, constraints=[constraint])

            # Add error
            if not valid:
                message_substitutions = {
                    'value': '"{}"'.format(value),
                    'constraint': '"{}"'.format(field.constraints[constraint]),
                }

                error = Error(
                    check,
                    cell,
                    message_substitutions=message_substitutions
                )
                errors.append(error)

        return errors

    return _check_constraint
