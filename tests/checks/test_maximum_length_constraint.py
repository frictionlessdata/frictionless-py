# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_maximum_length_constraint(log):
    source = [
        ['row', 'word'],
        [2, 'a'],
        [3, 'ab'],
        [4, 'abc'],
        [5, 'abcd'],
        [6],
    ]
    schema = {'fields': [
        {'name': 'row', 'type': 'integer'},
        {'name': 'word', 'type': 'string', 'constraints': {'maxLength': 2}}
    ]}
    report = validate(source, schema=schema, checks=[
        'maximum-length-constraint',
    ])
    assert log(report) == [
        (1, 4, 2, 'maximum-length-constraint'),
        (1, 5, 2, 'maximum-length-constraint'),
    ]
