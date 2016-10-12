# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_missing_value():
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'number': 2,
         'header': 'name2',
         'value': 'value',
         'field': None},
    ]
    checks.missing_value(errors, columns, 1)
    assert len(errors) == 0
    assert len(columns) == 2


def test_missing_value_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'number': 2,
         'header': 'name2',
         'field': None},
    ]
    checks.missing_value(errors, columns, 1)
    assert log(errors) == [
        (1, 2, 'missing-value'),
    ]
    assert len(columns) == 1
