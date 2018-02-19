# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from .constraints_checks import create_check_constraint


# Module API

@check('enumerable-constraint')
def enumerable_constraint(cells):
    return _check_constraint(cells)


_check_constraint = create_check_constraint('enumerable-constraint', 'enum')
