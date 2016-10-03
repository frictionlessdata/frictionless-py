# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_unordered_headers():
    fields = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name2'})},
        {'number': 3, 'header': 'name3'},
    ]
    assert checks.unordered_headers(fields) == []
    assert len(fields) == 3


def test_unordered_headers_problem():
    fields = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name2'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name1'})},
        {'number': 3, 'header': 'name3'},
    ]
    assert checks.unordered_headers(fields) == [
        {'message': 'Unordered headers', 'row-number': None, 'col-number': 1},
        {'message': 'Unordered headers', 'row-number': None, 'col-number': 2},
    ]
    assert len(fields) == 1
