# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_row import DuplicateRow


# Test

def test_check_duplicate_row(log):
    errors = []
    columns1 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': None},
    ]
    columns2 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value2',
         'field': None},
    ]
    duplicate_row = DuplicateRow()
    duplicate_row.check_row(errors, columns1, 1)
    duplicate_row.check_row(errors, columns2, 2)
    assert log(errors) == []
    assert len(columns1) == 1
    assert len(columns2) == 1


def test_check_duplicate_row_problem(log):
    errors = []
    columns1 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    columns2 = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    duplicate_row = DuplicateRow()
    duplicate_row.check_row(errors, columns1, 1)
    duplicate_row.check_row(errors, columns2, 2)
    assert log(errors) == [
        (2, None, 'duplicate-row'),
    ]
    assert len(columns1) == 1
    assert len(columns2) == 0
