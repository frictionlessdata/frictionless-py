# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import checks


# Test

def test_blank_header_good():
    columns = [
        {'number': 1, 'header': 'name', 'field': None},
    ]
    assert checks.blank_header(columns) == []


def test_blank_header_bad():
    columns = [
        {'number': 1, 'header': '', 'field': None},
    ]
    assert checks.blank_header(columns) == [
        {'message': 'Blank header', 'row-number': None, 'col-number': 1},
    ]
