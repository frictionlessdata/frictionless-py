# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.type_or_format_error import type_or_format_error
import goodtables.cells


# Check

def test_check_type_or_format_error(log):
    field = Field({'name': 'name', 'type': 'integer'})
    cells = [
        goodtables.cells.create_cell('name1', '1', field, column_number=1)
    ]
    errors = type_or_format_error(cells)
    assert log(errors) == []
    assert len(cells) == 1


def test_check_type_or_format_error_problem(log):
    field = Field({'name': 'name', 'type': 'integer'})
    cells = [
        goodtables.cells.create_cell('name1', 'value1', field, column_number=1, row_number=1)
    ]
    errors = type_or_format_error(cells)
    assert log(errors) == [
        (1, 1, 'type-or-format-error'),
    ]
    assert len(cells) == 0
