# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_extra_header():
    errors = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name2'})},
    ]
    sample = []
    checks.extra_header(errors, columns, sample=sample)
    assert len(errors) == 0
    assert len(columns) == 2


def test_extra_header_problem():
    errors = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2'},
    ]
    sample = []
    checks.extra_header(errors, columns, sample=sample, infer_fields=True)
    assert errors == [
        {'code': 'extra-header',
         'message': 'Extra header',
         'row-number': None,
         'column-number': 2},
    ]
    assert len(columns) == 2
    assert columns[1]['field'].name == 'name2'
