# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import profiles


# Test

def test_datapackage():
    errors = []
    tables = []
    profiles.datapackage(errors, tables, 'data/datapackages/valid/datapackage.json')
    assert len(errors) == 0
    assert len(tables) == 2
