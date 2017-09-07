# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from goodtables import Inspector


# Preset: table

def test_inspector_table_valid(log):
    inspector = Inspector()
    report = inspector.inspect('data/valid.csv')
    assert log(report) == []


def test_inspector_table_invalid(log):
    inspector = Inspector(infer_schema=True)
    report = inspector.inspect('data/invalid.csv')
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 4, 'duplicate-header'),
        (1, 2, 3, 'missing-value'),
        (1, 2, 4, 'missing-value'),
        (1, 3, None, 'duplicate-row'),
        (1, 4, None, 'blank-row'),
        (1, 5, 3, 'type-or-format-error'),
        (1, 5, 4, 'type-or-format-error'),
        (1, 5, 5, 'extra-value'),
    ]


def test_inspector_table_invalid_error_limit(log):
    inspector = Inspector(error_limit=2, infer_schema=True)
    report = inspector.inspect('data/invalid.csv')
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 4, 'duplicate-header'),
    ]


def test_inspector_table_invalid_row_limit(log):
    inspector = Inspector(row_limit=2, infer_schema=True)
    report = inspector.inspect('data/invalid.csv')
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 4, 'duplicate-header'),
        (1, 2, 3, 'missing-value'),
        (1, 2, 4, 'missing-value'),
    ]


# Preset: datapackage

def test_inspector_datapackage_valid(log):
    inspector = Inspector()
    report = inspector.inspect(
        'data/datapackages/valid/datapackage.json', preset='datapackage')
    assert log(report) == []


def test_inspector_datapackage_invalid(log):
    inspector = Inspector()
    report = inspector.inspect(
        'data/datapackages/invalid/datapackage.json', preset='datapackage')
    assert log(report) == [
        (1, 3, None, 'blank-row'),
        (2, 4, None, 'blank-row'),
    ]


def test_inspector_datapackage_invalid_table_limit(log):
    inspector = Inspector(table_limit=1)
    report = inspector.inspect(
        'data/datapackages/invalid/datapackage.json', preset='datapackage')
    assert log(report) == [
        (1, 3, None, 'blank-row'),
    ]


# Preset: nested

def test_inspector_tables_invalid(log):
    inspector = Inspector(infer_schema=True)
    report = inspector.inspect([
        {'source': 'data/valid.csv',
         'schema': {'fields': [{'name': 'id'}, {'name': 'name'}]}},
        {'source': 'data/invalid.csv'},
    ], preset='nested')
    assert log(report) == [
        (2, None, 3, 'blank-header'),
        (2, None, 4, 'duplicate-header'),
        (2, 2, 3, 'missing-value'),
        (2, 2, 4, 'missing-value'),
        (2, 3, None, 'duplicate-row'),
        (2, 4, None, 'blank-row'),
        (2, 5, 3, 'type-or-format-error'),
        (2, 5, 4, 'type-or-format-error'),
        (2, 5, 5, 'extra-value'),
    ]


# Catch exceptions

def test_inspector_catch_all_open_exceptions(log):
    inspector = Inspector()
    report = inspector.inspect('data/latin1.csv', encoding='utf-8')
    assert log(report) == [
        (1, None, None, 'source-error'),
    ]


def test_inspector_catch_all_iter_exceptions(log):
    inspector = Inspector()
    # Reducing sample size to get raise on iter, not on open
    report = inspector.inspect([['h'], [1], 'bad'], sample_size=1)
    assert log(report) == [
        (1, None, None, 'source-error'),
    ]


# Warnings

def test_inspector_warnings_no():
    inspector = Inspector()
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 0


def test_inspector_warnings_bad_datapackage_json():
    inspector = Inspector()
    source = 'data/invalid_json.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 1
    assert 'Unable to parse JSON' in report['warnings'][0]


def test_inspector_warnings_table_limit():
    inspector = Inspector(table_limit=1)
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 1
    assert 'table(s) limit' in report['warnings'][0]


def test_inspector_warnings_row_limit():
    inspector = Inspector(row_limit=1)
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 2
    assert 'row(s) limit' in report['warnings'][0]
    assert 'row(s) limit' in report['warnings'][1]


def test_inspector_warnings_error_limit():
    inspector = Inspector(error_limit=1)
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 2
    assert 'error(s) limit' in report['warnings'][0]
    assert 'error(s) limit' in report['warnings'][1]


def test_inspector_warnings_table_and_row_limit():
    inspector = Inspector(table_limit=1, row_limit=1)
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 2
    assert 'table(s) limit' in report['warnings'][0]
    assert 'row(s) limit' in report['warnings'][1]


def test_inspector_warnings_table_and_error_limit():
    inspector = Inspector(table_limit=1, error_limit=1)
    source = 'data/datapackages/invalid/datapackage.json'
    report = inspector.inspect(source, preset='datapackage')
    assert len(report['warnings']) == 2
    assert 'table(s) limit' in report['warnings'][0]
    assert 'error(s) limit' in report['warnings'][1]


# Empty source

def test_inspector_empty_source():
    inspector = Inspector()
    report = inspector.inspect('data/empty.csv')
    assert report['tables'][0]['row-count'] == 0
    assert report['tables'][0]['error-count'] == 0


# No headers source

def test_inspector_no_headers():
    inspector = Inspector()
    report = inspector.inspect('data/invalid_no_headers.csv', headers=None)
    assert report['tables'][0]['row-count'] == 3
    assert report['tables'][0]['error-count'] == 1
    assert report['tables'][0]['errors'][0]['code'] == 'extra-value'
