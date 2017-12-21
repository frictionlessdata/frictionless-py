# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from goodtables import validate, exceptions


# Validate

def test_check_deviated_value(log):
    source = [
        ['temperature'],
        [1],
        [-2],
        [7],
        [0],
        [1],
        [2],
        [5],
        [-4],
        [100],
        [8],
        [3],
    ]
    report = validate(source, checks=[
        {'deviated-value': {'column': 'temperature', 'average': 'median', 'interval': 3}},
    ])
    assert log(report) == [
        (1, 10, 1, 'deviated-value'),
    ]


def test_check_deviated_value_not_enough_data(log):
    source = [
        ['temperature'],
        [1],
    ]
    report = validate(source, checks=[
        {'deviated-value': {'column': 'temperature'}},
    ])
    assert log(report) == []


def test_check_deviated_value_not_a_number(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(source, checks=[
        {'deviated-value': {'column': 'name'}},
    ])
    assert log(report) == [
        (1, 2, 2, 'deviated-value'),
    ]


def test_check_deviated_value_non_existent_column(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    report = validate(source, checks=[
        {'deviated-value': {'column': 3}},
        {'deviated-value': {'column': 'non-existent'}},
    ])
    assert log(report) == [
        (1, 2, None, 'deviated-value'),
        (1, 2, None, 'deviated-value'),
    ]


def test_check_deviated_value_incorrect_average(log):
    source = [
        ['row', 'name'],
        [2, 'Alex'],
    ]
    with pytest.raises(exceptions.GoodtablesException):
        report = validate(source, checks=[
            {'deviated-value': {'column': 3, 'average': 'incorrect-average'}},
        ])
