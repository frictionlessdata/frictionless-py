# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from .constraints_checks import create_check_constraint


# Module API

@check('maximum-length-constraint', type='schema', context='body')
def maximum_length_constraint(cells, row_number):
    check_constraint = create_check_constraint('maximum-length-constraint', 'maxLength')
    return check_constraint(cells, row_number)
