# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_duplicate_header_good():
    errors = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': None},
        {'number': 2, 'header': 'name2', 'field': None},
    ]
    checks.duplicate_header(errors, columns)
    assert len(errors) == 0
    assert len(columns) == 2


def test_duplicate_header_bad():
    errors = []
    columns = [
        {'number': 1, 'header': 'name', 'field': None},
        {'number': 2, 'header': 'name', 'field': None},
    ]
    checks.duplicate_header(errors, columns)
    assert errors == [
        {'code': 'duplicate-header',
         'message': 'Duplicate header',
         'row-number': None,
         'column-number': 2},
    ]
    assert len(columns) == 2
