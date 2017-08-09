# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_custom_constraint(log):
    source = [
        ['row', 'salary', 'bonus'],
        [2, 1000, 200],
        [3, 2500, 500],
        [4, 1300, 500],
        [5, 5000, 1000],
        [6],
    ]
    report = validate(source, checks=[
        {'custom-constraint': {'constraint': 'salary > bonus * 4'}},
    ])
    assert log(report) == [
        (1, 4, None, 'custom-constraint'),
        (1, 6, None, 'custom-constraint'),
    ]


def test_check_custom_constraint_incorrect_constraint(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(source, checks=[
        {'custom-constraint': {'constraint': 'vars()'}},
        {'custom-constraint': {'constraint': 'import(os)'}},
        {'custom-constraint': {'constraint': 'non_existent > 0'}},
    ])
    assert log(report) == [
        (1, 2, None, 'custom-constraint'),
        (1, 2, None, 'custom-constraint'),
        (1, 2, None, 'custom-constraint'),
    ]
