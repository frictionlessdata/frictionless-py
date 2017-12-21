# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
import goodtables.cells
from goodtables.checks.extra_value import ExtraValue


# Check

def test_check_extra_value(log):
    cells = [
        goodtables.cells.create_cell('name1', 'value'),
        goodtables.cells.create_cell('name2', 'value'),
    ]
    extra_value = ExtraValue()
    errors = extra_value.check_row(cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_extra_value_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', 'value', row_number=1, column_number=1),
        goodtables.cells.create_cell(None, 'value', row_number=1, column_number=2),
    ]
    extra_value = ExtraValue()
    errors = extra_value.check_row(cells)
    assert log(errors) == [
        (1, 2, 'extra-value'),
    ]
    assert len(cells) == 1
