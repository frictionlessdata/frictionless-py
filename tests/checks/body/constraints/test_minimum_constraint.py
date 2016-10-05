# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_minimum_constraint():
    columns = []
    assert checks.minimum_constraint(1, columns) == []
