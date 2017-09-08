# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import pytest
from goodtables import validate


# Infer preset

def test_validate_infer_table(log):
    report = validate('data/invalid.csv')
    assert report['error-count'] == 7


def test_validate_infer_datapackage_path(log):
    report = validate('data/datapackages/invalid/datapackage.json')
    assert report['error-count'] == 2


def test_validate_infer_datapackage_dict(log):
    with open('data/datapackages/invalid/datapackage.json') as file:
        report = validate(json.load(file))
        assert report['error-count'] == 2


def test_validate_infer_nested(log):
    report = validate([{'source': 'data/invalid.csv'}])
    assert report['error-count'] == 7


# Report's preset

def test_validate_report_scheme_format_encoding():
    report = validate('data/valid.csv')
    assert report['preset'] == 'table'


# Report's scheme/format/encoding

def test_validate_report_scheme_format_encoding():
    report = validate('data/valid.csv')
    assert report['tables'][0]['scheme'] == 'file'
    assert report['tables'][0]['format'] == 'csv'
    assert report['tables'][0]['encoding'] == 'utf-8'


# Report's schema

def test_validate_report_schema():
    report = validate('data/valid.csv')
    assert report['tables'][0]['schema'] == None


def test_validate_report_schema_infer_schema():
    report = validate('data/valid.csv', infer_schema=True)
    assert report['tables'][0]['schema'] == 'table-schema'


# Nested source with individual checks

def test_validate_nested_checks(log):
    source = [
        ['field'],
        ['value', 'value'],
        [''],
    ]
    report = validate([
        {'source': source, 'checks': ['extra-value']},
        {'source': source, 'checks': ['blank-row']}
    ])
    assert log(report) == [
        (1, 2, 2, 'extra-value'),
        (2, 3, None, 'blank-row'),
    ]


# Invalid table schema

def test_validate_invalid_table_schema(log):
    source = [
        ['name', 'age'],
        ['Alex', '33'],
    ]
    schema = {'fields': [
        {'name': 'name'},
        {'name': 'age', 'type': 'bad'},
    ]}
    report = validate(source, schema=schema)
    assert log(report) == [
        (1, None, None, 'schema-error'),
    ]


# Datapackage with css dialect header false

def test_validate_datapackage_dialect_header_false(log):
    descriptor = {
        'resources': [
            {
                'name': 'name',
                'data': [
                    ['John', '22'],
                    ['Alex', '33'],
                    ['Paul', '44'],
                ],
                'schema': {
                    'fields': [
                        {'name': 'name'},
                        {'name': 'age', 'type': 'integer'},
                    ]
                },
                'dialect': {
                    'header': False,
                }
            }
        ]
    }
    report = validate(descriptor)
    assert log(report) == []
