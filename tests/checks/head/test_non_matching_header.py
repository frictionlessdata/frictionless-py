# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_non_matching_header():
    fields = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name1'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name2'})},
        {'number': 3, 'header': 'name3'},
    ]
    assert checks.non_matching_header(fields) == []
    assert len(fields) == 3


def test_non_matching_header_problem():
    fields = [
        {'number': 1, 'header': 'name1', 'field': Field({'name': 'name2'})},
        {'number': 2, 'header': 'name2', 'field': Field({'name': 'name1'})},
        {'number': 3, 'header': 'name3'},
    ]
    assert checks.non_matching_header(fields) == [
        {'message': 'Non matching header', 'row-number': None, 'column-number': 1},
        {'message': 'Non matching header', 'row-number': None, 'column-number': 2},
    ]
    assert len(fields) == 1
