# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables.checks.non_castable_value import non_castable_value


# Check

def test_check_non_castable_value(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': '1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    non_castable_value(errors, cells, 1)
    assert log(errors) == []
    assert len(cells) == 1
    assert cells[0]['value'] == 1


def test_check_non_castable_value_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    non_castable_value(errors, cells, 1)
    assert log(errors) == [
        (1, 1, 'non-castable-value'),
    ]
    assert len(cells) == 0
