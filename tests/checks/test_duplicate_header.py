# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.checks.duplicate_header import duplicate_header
import goodtables.cells


# Check

def test_check_duplicate_header(log):
    cells = [
        goodtables.cells.create_cell('name1', column_number=1),
        goodtables.cells.create_cell('name2', column_number=2),
    ]
    errors = duplicate_header(cells)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_duplicate_header_problem(log):
    cells = [
        goodtables.cells.create_cell('name', column_number=1),
        goodtables.cells.create_cell('name', column_number=2),
    ]
    errors = duplicate_header(cells)
    assert log(errors) == [
        (None, 2, 'duplicate-header'),
    ]
    assert len(cells) == 2


def test_check_duplicate_headers_show_all_duplicates_except_the_first():
    cells = [
        goodtables.cells.create_cell('name', column_number=1),
        goodtables.cells.create_cell('name', column_number=2),
        goodtables.cells.create_cell('name', column_number=3),
    ]
    errors = duplicate_header(cells)

    assert '1, 3' in errors[0].message
    assert '1, 2' in errors[1].message
