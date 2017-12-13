# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_header import duplicate_header


# Check

def test_check_duplicate_header(log):
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': None},
        {'number': 2,
         'header': 'name2',
         'field': None},
    ]
    errors = duplicate_header(cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_duplicate_header_problem(log):
    cells = [
        {'number': 1,
         'header': 'name',
         'field': None},
        {'number': 2,
         'header': 'name',
         'field': None},
    ]
    errors = duplicate_header(cells)
    assert log(errors) == [
        (None, 2, 'duplicate-header'),
    ]
    assert len(cells) == 2


def test_check_duplicate_headers_show_all_duplicates_except_the_first():
    cells = [
        {'number': 1,
         'header': 'name',
         'field': None},
        {'number': 2,
         'header': 'name',
         'field': None},
        {'number': 3,
         'header': 'name',
         'field': None},
    ]
    errors = duplicate_header(cells)

    assert '1, 3' in errors[0].message
    assert '1, 2' in errors[1].message
