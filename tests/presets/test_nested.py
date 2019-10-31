# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from goodtables import validate
from goodtables.presets.table import table
from goodtables.presets.datapackage import datapackage
from goodtables.presets.nested import nested


# Validate

def test_validate_tables_invalid(log):
    report = validate([
        {'source': 'data/valid.csv',
         'schema': {'fields': [{'name': 'id'}, {'name': 'name'}]}},
        {'source': 'data/invalid.csv'},
    ], preset='nested', infer_schema=True)
    assert log(report) == [
        (2, None, 3, 'blank-header'),
        (2, None, 4, 'duplicate-header'),
        (2, 2, 3, 'missing-value'),
        (2, 2, 4, 'missing-value'),
        (2, 3, None, 'duplicate-row'),
        (2, 4, None, 'blank-row'),
        (2, 5, 5, 'extra-value'),
    ]


def test_validate_nested_presets_set_default_preset():
    report = validate([
        {'source': 'data/datapackages/valid/datapackage.json'},
    ], preset='nested', infer_schema=True)
    assert report['valid']
    assert report['warnings'] == []


# Preset

def test_preset_nested():
    warnings, tables = nested([
        {'source': 'data/valid.csv'},
        {'source': 'data/invalid.csv', 'preset': 'table'},
        {'source': 'data/datapackages/valid/datapackage.json', 'preset': 'datapackage'},
        {'source': 'data/datapackages/invalid/datapackage.json', 'preset': 'datapackage'},
    ], presets={
        'table': {'func': table},
        'nested': {'func': nested},
        'datapackage': {'func': datapackage},
    })
    assert len(warnings) == 0
    assert len(tables) == 6
