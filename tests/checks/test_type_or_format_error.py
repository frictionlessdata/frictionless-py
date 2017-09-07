# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.type_or_format_error import type_or_format_error


# Check

def test_check_type_or_format_error(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': '1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    type_or_format_error(errors, cells, 1)
    assert log(errors) == []
    assert len(cells) == 1
    assert cells[0]['value'] == 1


def test_check_type_or_format_error_problem(log):
    errors = []
    cells = [
        {'number': 1,
         'header': 'name1',
         'value': 'value1',
         'field': Field({'name': 'name', 'type': 'integer'})},
    ]
    type_or_format_error(errors, cells, 1)
    assert log(errors) == [
        (1, 1, 'type-or-format-error'),
    ]
    assert len(cells) == 0
