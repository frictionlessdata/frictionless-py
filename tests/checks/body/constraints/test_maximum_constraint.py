# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_maximum_constraint(log):
    errors = []
    columns = []
    checks.maximum_constraint(errors, columns, 1)
    assert log(errors) == []
    assert len(columns) == 0
