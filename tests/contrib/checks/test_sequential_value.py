# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_sequential_value(log):
    source = [
        ['row', 'index2', 'index3'],
        [2, 1, 1],
        [3, 2, 3],
        [4, 3, 5],
        [5, 5, 6],
        [6],
    ]
    report = validate(source, checks=[
        {'sequential-value': {'column': 2}},
        {'sequential-value': {'column': 'index3'}},
    ])
    assert log(report) == [
        (1, 3, 3, 'sequential-value'),
        (1, 4, 3, 'sequential-value'),
        (1, 5, 2, 'sequential-value'),
        (1, 6, 2, 'sequential-value'),
        (1, 6, 3, 'sequential-value'),
    ]


def test_check_sequential_value_non_existent_column(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(source, checks=[
        {'sequential-value': {'column': 3}},
        {'sequential-value': {'column': 'non-existent'}},
    ])
    assert log(report) == [
        (1, 2, None, 'sequential-value'),
        (1, 2, None, 'sequential-value'),
    ]
