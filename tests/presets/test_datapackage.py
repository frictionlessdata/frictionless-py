# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from copy import deepcopy
from goodtables import validate
from goodtables.presets.datapackage import datapackage


# Validate

@pytest.mark.parametrize('dp_path', [
    'data/datapackages/valid/datapackage.json',
    'data/datapackages/valid.zip',
])
def test_validate_datapackage_valid(log, dp_path):
    report = validate(dp_path)
    assert log(report) == []


@pytest.mark.parametrize('dp_path', [
    'data/datapackages/invalid/datapackage.json',
    'data/datapackages/invalid.zip',
])
def test_validate_datapackage_invalid(log, dp_path):
    report = validate(dp_path)
    assert log(report) == [
        (1, 3, None, 'blank-row'),
        (2, 4, None, 'blank-row'),
    ]


# Validate (integrity)

DESCRIPTOR = {
    'resources': [
        {
            'name': 'resource1',
            'path': 'data/valid.csv',
            'bytes': 30,
            'hash': 'sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8',
        }
    ]
}

def test_check_file_integrity(log):
    source = deepcopy(DESCRIPTOR)
    report = validate(source)
    assert log(report) == []


def test_check_file_integrity_invalid(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['bytes'] += 1
    source['resources'][0]['hash'] += 'a'
    report = validate(source)
    assert report['tables'][0]['errors'] == [{
        'code': 'source-error',
        'message': 'Calculated size "30" and hash "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8" differ(s) from declared value(s)',
        'message-data': {}
    }]


def test_check_file_integrity_size(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['hash'] = None
    report = validate(source)
    assert log(report) == []


def test_check_file_integrity_size_invalid(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['bytes'] += 1
    source['resources'][0]['hash'] = None
    report = validate(source)
    assert report['tables'][0]['errors'] == [{
        'code': 'source-error',
        'message': 'Calculated size "30" differ(s) from declared value(s)',
        'message-data': {}
    }]


def test_check_file_integrity_hash(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['bytes'] = None
    report = validate(source)
    assert log(report) == []


def test_check_file_integrity_hash_invalid(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['bytes'] = None
    source['resources'][0]['hash'] += 'a'
    report = validate(source)
    assert report['tables'][0]['errors'] == [{
        'code': 'source-error',
        'message': 'Calculated hash "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8" differ(s) from declared value(s)',
        'message-data': {}
    }]


def test_check_file_integrity_invalid(log):
    source = deepcopy(DESCRIPTOR)
    source['resources'][0]['hash'] = 'not-supported-hash'
    report = validate(source)
    assert report['warnings'] == [
        'Resource "resource1" does not use the SHA256 hash. The check will be skipped',
    ]


# Preset

def test_preset_datapackage():
    warnings, tables = datapackage('data/datapackages/valid/datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 2


# Issues

def test_preset_datapackage_non_tabular_datapackage_issue_170():
    warnings, tables = datapackage('data/non_tabular_datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 2


def test_preset_datapackage_mixed_datapackage_issue_170():
    warnings, tables = datapackage('data/mixed_datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 2


def test_preset_datapackage_invalid_json_issue_192():
    warnings, tables = datapackage('data/invalid_json.json')
    assert len(warnings) == 1
    assert len(tables) == 0
    assert 'Unable to parse JSON' in warnings[0]
