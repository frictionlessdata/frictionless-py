# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_extra_value():
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
    assert checks.extra_value(1, columns) == []
    assert len(columns) == 2


def test_extra_value_problem():
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
        {'number': 2,
         'value': 'value'},
    ]
    assert checks.extra_value(1, columns) == [
        {'message': 'Extra value', 'row-number': 1, 'col-number': 2, },
    ]
    assert len(columns) == 1
