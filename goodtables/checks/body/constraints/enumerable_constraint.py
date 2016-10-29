# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ....register import check


# Module API

@check('enumerable-constraint')
def enumerable_constraint(errors, columns, row_number, state=None):
    for column in columns:
        if len(column) == 4:
            valid = column['field'].test_value(column['value'], constraint='enum')
            if not valid:
                # Add error
                message = 'Row %s has enum constraint violation in column %s'
                message = message % (row_number, column['number'])
                errors.append({
                    'code': 'enumerable-constraint',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })
