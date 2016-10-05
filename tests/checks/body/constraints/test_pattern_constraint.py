# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_pattern_constraint():
    columns = []
    assert checks.pattern_constraint(1, columns) == []
