# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import presets


# Test

def test_tables():
    errors, tables = presets.tables([
        {'source': 'data/valid.csv'},
        {'source': 'data/invalid.csv'},
    ])
    assert len(errors) == 0
    assert len(tables) == 2
