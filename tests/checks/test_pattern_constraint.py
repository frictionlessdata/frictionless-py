# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.pattern_constraint import pattern_constraint


# Test

def test_check_pattern_constraint(log):
    errors = []
    columns = []
    pattern_constraint(errors, columns, 1)
    assert log(errors) == []
    assert len(columns) == 0
