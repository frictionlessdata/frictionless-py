# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import presets


# Test

def test_preset_datapackage():
    warnings, tables = presets.datapackage('data/datapackages/valid/datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 2


def test_preset_datapackage_non_tabular_datapackage_issue_170():
    warnings, tables = presets.datapackage('data/non_tabular_datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 0


def test_preset_datapackage_mixed_datapackage_issue_170():
    warnings, tables = presets.datapackage('data/mixed_datapackage.json')
    assert len(warnings) == 0
    assert len(tables) == 1


def test_preset_datapackage_invalid_json_issue_192():
    warnings, tables = presets.datapackage('data/invalid_json.json')
    assert len(warnings) == 1
    assert len(tables) == 0
    assert 'Unable to parse JSON' in warnings[0]
