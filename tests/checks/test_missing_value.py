# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.missing_value import missing_value
import goodtables.cells


# Check

def test_check_missing_value(log):
    cells = [
        goodtables.cells.create_cell('name1', 'value', column_number=1),
        goodtables.cells.create_cell('name2', 'value', column_number=2),
    ]
    errors = missing_value(cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_missing_value_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', 'value', row_number=1, column_number=1),
        goodtables.cells.create_cell('name2', None, row_number=1, column_number=2),
    ]
    errors = missing_value(cells)
    assert log(errors) == [
        (1, 2, 'missing-value'),
    ]
    assert len(cells) == 1
