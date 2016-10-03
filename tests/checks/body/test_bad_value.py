# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_bad_value():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': '1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    assert checks.bad_value(cells) == []
    assert cells[0]['value'] == 1
    assert len(cells) == 1


def test_bad_value_problem():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    assert checks.bad_value(cells) == [
        {'message': 'Bad value', 'row-number': 1,  'col-number': 1},
    ]
    assert len(cells) == 0
