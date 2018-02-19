# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.blank_row import blank_row
import goodtables.cells


# Check

def test_check_blank_row(log):
    cells = [
        goodtables.cells.create_cell('name1', 'value', row_number=1),
    ]
    errors = blank_row(cells)
    assert log(errors) == []
    assert len(cells) == 1


def test_check_blank_row_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', '', row_number=1),
    ]
    errors = blank_row(cells)
    assert log(errors) == [
        (1, None, 'blank-row'),
    ]
    assert len(cells) == 0
