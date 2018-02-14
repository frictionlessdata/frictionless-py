# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.missing_header import missing_header
import goodtables.cells


# Check

def test_check_missing_header(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name1'}), column_number=1),
        goodtables.cells.create_cell('name2', field=Field({'name': 'name2'}), column_number=2),
    ]
    errors = missing_header(cells, None)
    assert log(errors) == []
    assert len(cells) == 2


def test_check_missing_header_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name1'}), column_number=1),
        goodtables.cells.create_cell(None, field=Field({'name': 'name2'}), column_number=2),
    ]
    errors = missing_header(cells, None)
    assert log(errors) == [
        (None, 2, 'missing-header'),
    ]
    assert len(cells) == 1
