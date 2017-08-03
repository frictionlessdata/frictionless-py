# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

def test_check_truncated_value(log):
    source = [
        ['row', 'name', 'salary'],
        [2, 'a' * 255, 32766 ],
        [3, 'John', 32767],
        [4, 'Sam', 2147483647],
        [5],
    ]
    report = validate(source, checks=[
        'truncated-value',
    ])
    assert log(report) == [
        (1, 2, 2, 'truncated-value'),
        (1, 3, 3, 'truncated-value'),
        (1, 4, 3, 'truncated-value'),
    ]
