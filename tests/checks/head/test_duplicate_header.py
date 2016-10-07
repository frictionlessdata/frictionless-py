# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_duplicate_header_good():
    columns = [
        {'number': 1, 'header': 'name1', 'field': None},
        {'number': 2, 'header': 'name2', 'field': None},
    ]
    assert checks.duplicate_header(columns) == []


def test_duplicate_header_bad():
    columns = [
        {'number': 1, 'header': 'name', 'field': None},
        {'number': 2, 'header': 'name', 'field': None},
    ]
    assert checks.duplicate_header(columns) == [
        {'message': 'Duplicate header', 'row-number': None, 'column-number': 2},
    ]
