# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_header import duplicate_header


# Check

def test_check_duplicate_header(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': None},
        {'number': 2,
         'header': 'name2',
         'field': None},
    ]
    duplicate_header(errors, cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_duplicate_header_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name',
         'field': None},
        {'number': 2,
         'header': 'name',
         'field': None},
    ]
    duplicate_header(errors, cells)
    assert log(errors) == [
        (None, 2, 'duplicate-header'),
    ]
    assert len(cells) == 2
