# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_missing_header():
    errors = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name2'})},
    ]
    checks.missing_header(errors, columns)
    assert len(errors) == 0
    assert len(columns) == 2


def test_missing_header_problem():
    errors = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'field': Field({'name': 'name2'})},
    ]
    checks.missing_header(errors, columns)
    assert errors == [
        {'code': 'missing-header',
         'message': 'Missing header',
         'row-number': None,
         'column-number': 2},
    ]
    assert len(columns) == 1
