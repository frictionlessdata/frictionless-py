# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_duplicate_row():
    state = {}
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
    assert checks.duplicate_row(1, columns1, state) == []
    assert checks.duplicate_row(2, columns2, state) == []


def test_duplicate_row_problem():
    state = {}
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
    assert checks.duplicate_row(1, columns1, state) == []
    assert checks.duplicate_row(2, columns2, state) == [
        {'message': 'Duplicate row: [1]', 'row-number': 2, 'column-number': None},
    ]
