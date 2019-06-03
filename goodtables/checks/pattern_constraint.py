# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ..registry import check
from .constraints_checks import create_check_constraint


# Module API

@check('pattern-constraint')
def pattern_constraint(cells):
    errors = _check_constraint(cells)

    for error in errors:
        # No reason to run other checks in this cell
        if hasattr(error, 'cell'):
            cells.remove(error.cell)

    return errors


_check_constraint = create_check_constraint('pattern-constraint', 'pattern')
