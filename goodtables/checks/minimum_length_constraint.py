# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from .constraints_checks import create_check_constraint


# Module API

@check('minimum-length-constraint')
def minimum_length_constraint(cells):
    check_constraint = create_check_constraint('minimum-length-constraint', 'minLength')
    return check_constraint(cells)
