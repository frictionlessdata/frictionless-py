# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Field
from goodtables import checks


# Test

def test_extra_header(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2',
         'field': Field({'name': 'name2'})},
    ]
    sample = []
    checks.extra_header(errors, columns, sample=sample)
    assert log(errors) == []
    assert len(columns) == 2


def test_extra_header_infer(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2'},
    ]
    sample = []
    checks.extra_header(errors, columns, sample=sample, infer_fields=True)
    assert log(errors) == []
    assert len(columns) == 2
    assert columns[1]['field'].name == 'name2'


def test_extra_header_problem(log):
    errors = []
    columns = [
        {'number': 1,
         'header': 'name1',
         'field': Field({'name': 'name1'})},
        {'number': 2,
         'header': 'name2'},
    ]
    sample = []
    checks.extra_header(errors, columns, sample=sample)
    assert log(errors) == [
        (None, 2, 'extra-header'),
    ]
    assert len(columns) == 1
