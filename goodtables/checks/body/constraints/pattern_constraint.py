# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ....registry import check


# Module API

@check('pattern-constraint')
def pattern_constraint(errors, columns, row_number, state=None):
    # https://github.com/frictionlessdata/goodtables-py/issues/116
    for column in columns:
        if len(column) == 4:
            pass
