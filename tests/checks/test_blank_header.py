# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_check_blank_header(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name',
         'field': None},
    ]
    checks.blank_header(errors, columns)
    assert log(errors) == []
    assert len(columns) == 1


def test_check_blank_header_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': '',
         'field': None},
    ]
    checks.blank_header(errors, columns)
    assert log(errors) == [
        (None, 1, 'blank-header'),
    ]
    assert len(columns) == 1
