# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_row import DuplicateRow
import goodtables.cells


# Check

def test_check_duplicate_row(log):
    row1 = [
        goodtables.cells.create_cell('name', 'value1', row_number=1, column_number=1)
    ]
    row2 = [
        goodtables.cells.create_cell('name', 'value2', row_number=2, column_number=1)
    ]
    duplicate_row = DuplicateRow()
    errors = duplicate_row.check_row(row1)
    errors += duplicate_row.check_row(row2)
    assert log(errors) == []
    assert len(row1) == 1
    assert len(row2) == 1


def test_check_duplicate_row_problem(log):
    row1 = [
        goodtables.cells.create_cell('name', 'value', row_number=1, column_number=1)
    ]
    row2 = [
        goodtables.cells.create_cell('name', 'value', row_number=2, column_number=1)
    ]
    duplicate_row = DuplicateRow()
    errors = duplicate_row.check_row(row1)
    errors += duplicate_row.check_row(row2)
    assert log(errors) == [
        (2, None, 'duplicate-row'),
    ]
    assert len(row1) == 1
    assert len(row2) == 0
