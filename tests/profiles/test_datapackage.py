# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import profiles


# Test

def test_datapackage():
    dataset = []
    errors = profiles.datapackage(dataset, 'data/datapackages/valid/datapackage.json')
    assert len(dataset) == 2
    assert len(errors) == 0
