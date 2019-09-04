# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import json
import pytest
from importlib import import_module
from goodtables import validate, init_datapackage


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
    assert report['tables'][0].get('schema') is None


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

# TODO: enable after
# https://github.com/frictionlessdata/goodtables-py/issues/304
@pytest.mark.skip
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


# Source as pathlib.Path

@pytest.mark.skipif(sys.version_info < (3, 4), reason='not supported')
def test_source_pathlib_path_table():
    pathlib = import_module('pathlib')
    report = validate(pathlib.Path('data/valid.csv'))
    assert report['table-count'] == 1
    assert report['valid']


@pytest.mark.skipif(sys.version_info < (3, 4), reason='not supported')
def test_source_pathlib_path_datapackage():
    pathlib = import_module('pathlib')
    report = validate(pathlib.Path('data/datapackages/valid/datapackage.json'))
    assert report['table-count'] == 2
    assert report['valid']


# Foreign Keys

FK_DESCRIPTOR = {
  'resources': [
    {
      'name': 'cities',
      'data': [
        ['id', 'name', 'prev_id'],
        [1, 'london', None],
        [2, 'paris', 1],
        [3, 'rome', 2],
        [4, 'rio', 3],
      ],
      'schema': {
        'fields': [
          {'name': 'id', 'type': 'integer'},
          {'name': 'name', 'type': 'string'},
          {'name': 'prev_id', 'type': 'integer'},
        ],
        'foreignKeys': [
          {
            'fields': 'id',
            'reference': {'resource': 'people', 'fields': 'label'},
          },
          {
            'fields': 'prev_id',
            'reference': {'resource': '', 'fields': 'id'},
          },
        ],
      },
    }, {
      'name': 'people',
      'data': [
        ['label', 'population'],
        [1, 8],
        [2, 2],
        [3, 3],
        [4, 6],
      ],
    },
  ],
}

def test_foreign_key(log):
    report = validate(FK_DESCRIPTOR, checks=['foreign-key'])
    assert log(report) == []


# Issues

def test_composite_primary_key_unique_issue_215(log):
    descriptor = {
        'resources': [
            {
                'name': 'name',
                'data':  [
                    ['id1', 'id2'],
                    ['a', '1'],
                    ['a', '2'],
                ],
                'schema': {
                    'fields': [
                        {'name': 'id1'},
                        {'name': 'id2'},
                    ],
                    'primaryKey': ['id1', 'id2']
                }
            }
        ],
    }
    report = validate(descriptor)
    assert log(report) == []


def test_composite_primary_key_not_unique_issue_215(log):
    descriptor = {
        'resources': [
            {
                'name': 'name',
                'data':  [
                    ['id1', 'id2'],
                    ['a', '1'],
                    ['a', '1'],
                ],
                'schema': {
                    'fields': [
                        {'name': 'id1'},
                        {'name': 'id2'},
                    ],
                    'primaryKey': ['id1', 'id2']
                }
            }
        ],
    }
    report = validate(descriptor, skip_checks=['duplicate-row'])
    assert log(report) == [
        (1, 3, 1, 'unique-constraint'),
    ]


def test_validate_infer_fields_issue_223():
    source = [
        ['name1', 'name2'],
        ['123', 'abc'],
        ['456', 'def'],
        ['789', 'ghi'],
    ]
    schema = {
        'fields': [{'name': 'name1'}]
    }
    report = validate(source, schema=schema, infer_fields=True)
    assert report['valid']

def test_validate_infer_fields_issue_225():
    source = [
        ['name1', 'name2'],
        ['123', ''],
        ['456', ''],
        ['789', ''],
    ]
    schema = {
        'fields': [{'name': 'name1'}]
    }
    report = validate(source, schema=schema, infer_fields=True)
    assert report['valid']



class TestValidateInitDatapackage(object):
    def test_datapackage_is_correct(self):
        resources_paths = [
            'data/valid.csv',
            'data/sequential_value.csv',
        ]
        dp = init_datapackage(resources_paths)

        assert dp is not None
        assert dp.valid, dp.errors
        assert len(dp.resources) == 2

        actual_resources_paths = [res.descriptor['path'] for res in dp.resources]
        assert sorted(resources_paths) == sorted(actual_resources_paths)
