# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.non_matching_header import NonMatchingHeader


# Check

def test_check_non_matching_header(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name2'})},
        {'number': 3,
         'header': 'name3'},
    ]
    non_matching_header = NonMatchingHeader()
    non_matching_header.check_headers(errors, cells)
    assert log(errors) == []
    assert len(cells) == 3


def test_check_non_matching_header_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name2'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    non_matching_header = NonMatchingHeader()
    non_matching_header.check_headers(errors, cells)
    assert log(errors) == [
        (None, 1, 'non-matching-header'),
        (None, 2, 'non-matching-header'),
    ]
    assert len(cells) == 1


def test_check_non_matching_header_order_fields(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name2'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    non_matching_header = NonMatchingHeader(order_fields=True)
    non_matching_header.check_headers(errors, cells)
    assert log(errors) == []
    assert len(cells) == 3


def test_check_non_matching_header_order_fields_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name4'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name1'})},
        {'number': 3,
         'header': 'name3'},
    ]
    non_matching_header = NonMatchingHeader(order_fields=True)
    non_matching_header.check_headers(errors, cells)
    assert log(errors) == [
        (None, 2, 'non-matching-header'),
    ]
    assert len(cells) == 2
