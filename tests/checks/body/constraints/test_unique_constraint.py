# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_unique_constraint():
    state = {}
    errors = []
    columns = []
    checks.unique_constraint(errors, columns, 1, state=state)
    assert len(errors) == 0
    assert len(columns) == 0
