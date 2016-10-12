# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_blank_row():
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    checks.blank_row(errors, columns, 1)
    assert len(errors) == 0
    assert len(columns) == 1


def test_blank_row_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': '',
         'field': None},
    ]
    checks.blank_row(errors, columns, 1)
    assert log(errors) == [
        (1, None, 'blank-row'),
    ]
    assert len(columns) == 0
