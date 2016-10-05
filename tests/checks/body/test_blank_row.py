# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_blank_row():
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    assert checks.blank_row(1, columns) == []


def test_blank_row_problem():
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': '',
         'field': None},
    ]
    assert checks.blank_row(1, columns) == [
        {'message': 'Blank row', 'row-number': 1, 'col-number': None},
    ]
    assert columns == []
