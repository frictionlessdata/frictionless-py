# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_blacklisted_value(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
        [3, 'John'],
        [4, 'mistake'],
        [5, 'error'],
        [6],
    ]
    report = validate(source, checks=[
        {'blacklisted-value': {'column': 1, 'blacklist': [10]}},
        {'blacklisted-value': {'column': 2, 'blacklist': ['mistake']}},
        {'blacklisted-value': {'column': 'row', 'blacklist': [10]}},
        {'blacklisted-value': {'column': 'name', 'blacklist': ['error']}},
    ])
    assert log(report) == [
        (1, 4, 2, 'blacklisted-value'),
        (1, 5, 2, 'blacklisted-value'),
    ]


def test_check_blacklisted_value_non_existent_column(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(source, checks=[
        {'blacklisted-value': {'column': 3, 'blacklist': [10]}},
        {'blacklisted-value': {'column': 'non-existent', 'blacklist': ['mistake']}},
    ])
    assert log(report) == [
        (1, 2, None, 'blacklisted-value'),
        (1, 2, None, 'blacklisted-value'),
    ]
