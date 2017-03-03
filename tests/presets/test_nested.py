# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import presets


# Test

def test_datapackages():
    errors, tables = presets.nested([
        {'source': 'data/valid.csv'},
        {'source': 'data/invalid.csv', 'preset': 'table'},
        {'source': 'data/datapackages/valid/datapackage.json', 'preset': 'datapackage'},
        {'source': 'data/datapackages/invalid/datapackage.json', 'preset': 'datapackage'},
    ], presets={
        'table': presets.table,
        'nested': presets.nested,
        'datapackage': presets.datapackage,
    })
    assert len(errors) == 0
    assert len(tables) == 6
