# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables.presets.table import table
from goodtables.presets.datapackage import datapackage
from goodtables.presets.nested import nested


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
