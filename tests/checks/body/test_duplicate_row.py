# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_duplicate_row():
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
    state = {}
    checks.duplicate_row(errors, columns1, 1, state=state)
    checks.duplicate_row(errors, columns2, 2, state=state)
    assert len(errors) == 0
    assert len(columns1) == 1
    assert len(columns2) == 1


def test_duplicate_row_problem():
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
    state = {}
    checks.duplicate_row(errors, columns1, 1, state=state)
    checks.duplicate_row(errors, columns2, 2, state=state)
    assert errors == [
        {'code': 'duplicate-row',
         'message': 'Duplicate row: [1]',
         'row-number': 2,
         'column-number': None},
    ]
    assert len(columns1) == 1
    assert len(columns2) == 0
