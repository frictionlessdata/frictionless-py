# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.blank_row import blank_row


# Test

def test_check_blank_row(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': 'value',
         'field': None},
    ]
    blank_row(errors, columns, 1)
    assert log(errors) == []
    assert len(columns) == 1


def test_check_blank_row_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'value': '',
         'field': None},
    ]
    blank_row(errors, columns, 1)
    assert log(errors) == [
        (1, None, 'blank-row'),
    ]
    assert len(columns) == 0
