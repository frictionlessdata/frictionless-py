# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks

# Test

def test_non_castable_value():
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': '1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    assert checks.non_castable_value(1, columns) == []
    assert columns[0]['value'] == 1
    assert len(columns) == 1


def test_non_castable_value_problem():
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    assert checks.non_castable_value(1, columns) == [
        {'message': 'Non castable value', 'row-number': 1,  'column-number': 1},
    ]
    assert len(columns) == 0
