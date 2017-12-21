# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
from goodtables.checks.unique_constraint import UniqueConstraint
import goodtables.cells


# Check

def test_check_unique_constraint(log):
    mock_field = mock.MagicMock()
    mock_field.descriptor = {'primaryKey': True}
    mock_field.constraints['unique'] = True
    cells1 = [
        goodtables.cells.create_cell('name', 'value', mock_field, row_number=1, column_number=1),
        goodtables.cells.create_cell('value', '50', mock_field, row_number=1, column_number=2),
    ]
    cells2 = [
        goodtables.cells.create_cell('name', 'value', mock_field, row_number=2, column_number=1),
        goodtables.cells.create_cell('value', '100', mock_field, row_number=2, column_number=2),
    ]
    duplicate_row = UniqueConstraint()
    errors = duplicate_row.check_row(cells1)
    errors += duplicate_row.check_row(cells2)

    assert log(errors) == [
        (2, 1, 'unique-constraint'),
    ]


def test_check_unique_constraint_works_without_data(log):
    cells = []
    unique_constraint = UniqueConstraint()
    errors = unique_constraint.check_row(cells)
    assert log(errors) == []
    assert len(cells) == 0
