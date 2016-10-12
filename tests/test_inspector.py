# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import Inspector


def test_inspector_table_valid(log):
    inspector = Inspector()
    report = inspector.inspect('data/valid.csv')
    assert log(report) == []


def test_inspector_table_invalid(log):
    inspector = Inspector()
    report = inspector.inspect('data/invalid.csv')
    assert log(report) == [
        (1, None, 3, 'blank-header'),
        (1, None, 4, 'duplicate-header'),
        (1, 2, 3, 'missing-value'),
        (1, 2, 4, 'missing-value'),
        (1, 3, None, 'duplicate-row'),
        (1, 4, None, 'blank-row'),
        (1, 5, 5, 'extra-value'),
        (1, 5, 3, 'non-castable-value'),
        (1, 5, 4, 'non-castable-value'),
    ]


def test_inspector_datapackage_valid(log):
    inspector = Inspector()
    report = inspector.inspect(
        'data/datapackages/valid/datapackage.json', profile='datapackage')
    assert log(report) == []


def test_inspector_datapackage_invalid(log):
    inspector = Inspector()
    report = inspector.inspect(
        'data/datapackages/invalid/datapackage.json', profile='datapackage')
    assert log(report) == [
        (1, 3, None, 'blank-row'),
        (2, 4, None, 'blank-row'),
    ]
