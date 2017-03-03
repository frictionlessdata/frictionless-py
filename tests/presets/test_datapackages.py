# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import presets


# Test

def test_datapackages():
    errors, tables = presets.datapackages([
        'data/datapackages/valid/datapackage.json',
        {'source': 'data/datapackages/invalid/datapackage.json'},
    ])
    assert len(errors) == 0
    assert len(tables) == 4
