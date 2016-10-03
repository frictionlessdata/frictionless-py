# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_blank_row():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    assert checks.blank_row(cells) == []


def test_blank_row_problem():
    cells = [
        {'row-number': 1,
         'col-number': 1,
         'header': 'name1',
         'value': '',
         'field': None},
    ]
    assert checks.blank_row(cells) == [
        {'message': 'Blank row', 'row-number': 1, 'col-number': None},
    ]
    assert cells == []
