# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.pattern_constraint import pattern_constraint


# Check

def test_check_pattern_constraint(log):
    cells = []
    errors = pattern_constraint(cells, 1)
    assert log(errors) == []
    assert len(cells) == 0
