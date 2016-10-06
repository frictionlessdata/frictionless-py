# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_extra_header():
    sample = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name2'})},
    ]
    assert checks.extra_header(columns, sample) == []


def test_extra_header_problem():
    sample = []
    columns = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2'},
    ]
    assert checks.extra_header(columns, sample, infer_fields=True) == [
        {'message': 'Extra header', 'row-number': None, 'col-number': 2},
    ]
    assert columns[1]['field'].name == 'name2'
