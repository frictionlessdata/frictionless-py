# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_check_non_matching_header(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name2'})},
        {'number': 3,
         'header': 'name3'},
    ]
    checks.non_matching_header(errors, columns)
    assert log(errors) == []
    assert len(columns) == 3


def test_check_non_matching_header_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name2'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    checks.non_matching_header(errors, columns)
    assert log(errors) == [
        (None, 1, 'non-matching-header'),
        (None, 2, 'non-matching-header'),
    ]
    assert len(columns) == 1


def test_check_non_matching_header_order_fields(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name2'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    checks.non_matching_header(errors, columns, order_fields=True)
    assert log(errors) == []
    assert len(columns) == 3


def test_check_non_matching_header_order_fields_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name4'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    checks.non_matching_header(errors, columns, order_fields=True)
    assert log(errors) == [
        (None, 2, 'non-matching-header'),
    ]
    assert len(columns) == 2
