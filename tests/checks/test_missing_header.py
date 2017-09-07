# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.missing_header import missing_header


# Check

def test_check_missing_header(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name2'})},
    ]
    missing_header(errors, cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_missing_header_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'field': Field({'name': 'name2'})},
    ]
    missing_header(errors, cells)
    assert log(errors) == [
        (None, 2, 'missing-header'),
    ]
    assert len(cells) == 1
