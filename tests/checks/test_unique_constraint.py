# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
from goodtables.checks.unique_constraint import UniqueConstraint


# Check

def test_check_unique_constraint(log):
    mock_field = mock.MagicMock()
    mock_field.descriptor = {'primaryKey': True}
    mock_field.constraints['unique'] = True
    cells1 = [
        {'number': 1,
         'header': 'name',
         'value': 'value',
         'field': mock_field},
        {'number': 2,
         'header': 'value',
         'value': '50',
         'field': mock_field},
    ]
    cells2 = [
        {'number': 1,
         'header': 'name',
         'value': 'value',
         'field': mock_field},
        {'number': 2,
         'header': 'value',
         'value': '100',
         'field': mock_field},
    ]
    duplicate_row = UniqueConstraint()
    errors = duplicate_row.check_row(cells1, 1)
    errors += duplicate_row.check_row(cells2, 2)

    assert log(errors) == [
        (2, 1, 'unique-constraint'),
    ]


def test_check_unique_constraint_works_without_data(log):
    cells = []
    unique_constraint = UniqueConstraint()
    errors = unique_constraint.check_row(cells, 1)
    assert log(errors) == []
    assert len(cells) == 0
