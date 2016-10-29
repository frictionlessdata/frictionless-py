# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ....register import check


# Module API

@check('unique-constraint')
def unique_constraint(errors, columns, row_number, state):
    rindexes = state.setdefault('cache', {})
    for column in columns:
        if len(column) == 4:
            if column['field'].constraints.get('unique'):
                rindex = rindexes.setdefault(column['number'], {})
                references = rindex.setdefault(column['value'], [])
                if references:
                    # Add error
                    mesrows = ', '.join(map(str, references + [row_number]))
                    message = 'Rows %s has unique constraint violation in column %s'
                    message = message % (mesrows, column['number'])
                    errors.append({
                        'code': 'unique-constraint',
                        'message': message,
                        'row-number': row_number,
                        'column-number': column['number'],
                    })
                references.append(row_number)
