# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Tests

def test_scenarios(log, name, scenario):
    expect = list(map(lambda item: tuple(item), scenario.pop('report')))
    actual = log(validate(**scenario))
    assert actual == expect
