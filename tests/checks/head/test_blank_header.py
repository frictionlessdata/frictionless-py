# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_blank_header_good():
    errors = []
    columns = [
        {'number': 1, 'header': 'name', 'field': None},
    ]
    checks.blank_header(errors, columns)
    assert len(errors) == 0
    assert len(columns) == 1


def test_blank_header_bad():
    errors = []
    columns = [
        {'number': 1, 'header': '', 'field': None},
    ]
    checks.blank_header(errors, columns)
    assert errors == [
        {'code': 'blank-header',
         'message': 'Blank header',
         'row-number': None,
         'column-number': 1},
    ]
    assert len(columns) == 1
