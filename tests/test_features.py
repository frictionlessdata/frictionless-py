# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Tests

def test_features(log, name, feature):
    expect = list(map(lambda item: tuple(item), feature.pop('report')))
    actual = log(validate(**feature))
    assert actual == expect
