# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from goodtables import validate
from goodtables.presets.table import table


# Validate


def test_validate_table_valid(log):
    report = validate('data/valid.csv')
    assert log(report) == []


def test_validate_table_invalid(log):
    report = validate('data/invalid.csv', infer_schema=True)
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 3, 'non-matching-header'),
        (1, None, 4, 'duplicate-header'),
        (1, None, 4, 'non-matching-header'),
        (1, 2, 3, 'missing-value'),
        (1, 2, 4, 'missing-value'),
        (1, 3, None, 'duplicate-row'),
        (1, 4, None, 'blank-row'),
        (1, 5, 5, 'extra-value'),
    ]


def test_validate_table_invalid_error_limit(log):
    report = validate('data/invalid.csv', error_limit=2, infer_schema=True)
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 4, 'duplicate-header'),
    ]


def test_validate_table_invalid_row_limit(log):
    report = validate('data/invalid.csv', row_limit=2, infer_schema=True)
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 3, 'non-matching-header'),
        (1, None, 4, 'duplicate-header'),
        (1, None, 4, 'non-matching-header'),
        (1, 2, 3, 'missing-value'),
        (1, 2, 4, 'missing-value'),
    ]


# Preset


def test_preset_table():
    warnings, tables = table('data/valid.csv')
    assert len(warnings) == 0
    assert len(tables) == 1


def test_preset_table_but_got_datapackage_issue_187():
    warnings, tables = table('data/datapackages/valid/datapackage.json')
    assert len(warnings) == 1
    assert len(tables) == 0
    assert 'Use "datapackage" preset' in warnings[0]


def test_preset_table_invalid_json_issue_196():
    warnings, tables = table('valid.csv', schema='data/invalid_json.json')
    assert len(warnings) == 1
    assert len(tables) == 0
    assert 'has a loading error' in warnings[0]
