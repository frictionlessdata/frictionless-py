# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.blank_row import blank_row


# Check

def test_check_blank_row(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    blank_row(errors, cells, 1)
    assert log(errors) == []
    assert len(cells) == 1


def test_check_blank_row_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': '',
         'field': None},
    ]
    blank_row(errors, cells, 1)
    assert log(errors) == [
        (1, None, 'blank-row'),
    ]
    assert len(cells) == 0
