# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.unique_constraint import UniqueConstraint


# Check

def test_check_unique_constraint(log):
    errors = []
    cells = []
    unique_constraint = UniqueConstraint()
    unique_constraint.check_row(errors, cells, 1)
    assert log(errors) == []
    assert len(cells) == 0
