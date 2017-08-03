# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.presets.table import table


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
