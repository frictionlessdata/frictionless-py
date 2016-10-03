# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_duplicate_row():
    state = {}
    cells1 = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': None},
    ]
    cells2 = [
        {'row-number': 2,
         'col-number': 1,
         'header': 'name1',
         'value': 'value2',
         'field': None},
    ]
    assert checks.duplicate_row(cells1, state) == []
    assert checks.duplicate_row(cells2, state) == []


def test_duplicate_row_problem():
    state = {}
    cells1 = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    cells2 = [
        {'row-number': 2,
         'col-number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    assert checks.duplicate_row(cells1, state) == []
    assert checks.duplicate_row(cells2, state) == [
        {'message': 'Duplicate row: [1]', 'row-number': 2, 'col-number': None},
    ]
