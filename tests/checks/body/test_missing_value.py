# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_missing_value():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'row-number': 1,
         'col-number': 2,
         'header': 'name2',
         'value': 'value',
         'field': None},
    ]
    assert checks.missing_value(cells) == []
    assert len(cells) == 2


def test_missing_value_problem():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'row-number': 1,
         'col-number': 2,
         'header': 'name2',
         'field': None},
    ]
    assert checks.missing_value(cells) == [
        {'message': 'Missing value', 'row-number': 1, 'col-number': 2},
    ]
    assert len(cells) == 1
