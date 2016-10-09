# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_extra_value():
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
    checks.extra_value(errors, columns, 1)
    assert len(errors) == 0
    assert len(columns) == 2


def test_extra_value_problem():
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'number': 2,
         'value': 'value'},
    ]
    checks.extra_value(errors, columns, 1)
    assert errors == [
        {'code': 'extra-value',
         'message': 'Extra value',
         'row-number': 1,
         'column-number': 2, },
    ]
    assert len(columns) == 1
