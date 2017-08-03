# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.minimum_constraint import minimum_constraint


# Check

def test_check_minimum_constraint(log):
    errors = []
    cells = []
    minimum_constraint(errors, cells, 1)
    assert log(errors) == []
    assert len(cells) == 0
