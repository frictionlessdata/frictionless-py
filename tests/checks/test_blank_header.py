# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.blank_header import blank_header
import goodtables.cells


# Check

def test_check_blank_header(log):
    errors = []
    cells = [
        goodtables.cells.create_cell('name'),
    ]
    errors = blank_header(cells)
    assert log(errors) == []
    assert len(cells) == 1


def test_check_blank_header_problem(log):
    errors = []
    cells = [
        goodtables.cells.create_cell('', column_number=1),
    ]
    errors = blank_header(cells)
    assert log(errors) == [
        (None, 1, 'blank-header'),
    ]
    assert len(cells) == 1
