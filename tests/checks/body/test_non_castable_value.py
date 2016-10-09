# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks

# Test

def test_non_castable_value():
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': '1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    checks.non_castable_value(errors, columns, 1)
    assert len(errors) == 0
    assert len(columns) == 1
    assert columns[0]['value'] == 1


def test_non_castable_value_problem():
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    checks.non_castable_value(errors, columns, 1)
    assert errors == [
        {'code': 'non-castable-value',
         'message': 'Non castable value',
         'row-number': 1,
         'column-number': 1},
    ]
    assert len(columns) == 0
