# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_minimum_constraint(log):
    source = [
        ['row', 'score'],
        [2, 1],
        [3, 2],
        [4, 3],
        [5, 4],
        [6],
    ]
    schema = {'fields': [
        {'name': 'row', 'type': 'string'},
        {'name': 'score', 'type': 'integer', 'constraints': {'minimum': 2}}
    ]}
    report = validate(source, schema=schema, checks=[
        'minimum-constraint',
    ])
    assert log(report) == [
        (1, 2, 2, 'minimum-constraint'),
    ]
