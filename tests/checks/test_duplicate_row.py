# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_row import DuplicateRow


# Check

def test_check_duplicate_row(log):
    errors = []
    cells1 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': None},
    ]
    cells2 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value2',
         'field': None},
    ]
    duplicate_row = DuplicateRow()
    duplicate_row.check_row(errors, cells1, 1)
    duplicate_row.check_row(errors, cells2, 2)
    assert log(errors) == []
    assert len(cells1) == 1
    assert len(cells2) == 1


def test_check_duplicate_row_problem(log):
    errors = []
    cells1 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    cells2 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    duplicate_row = DuplicateRow()
    duplicate_row.check_row(errors, cells1, 1)
    duplicate_row.check_row(errors, cells2, 2)
    assert log(errors) == [
        (2, None, 'duplicate-row'),
    ]
    assert len(cells1) == 1
    assert len(cells2) == 0
