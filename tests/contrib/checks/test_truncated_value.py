# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import pytest
import goodtables.cells
from goodtables import validate
from goodtables.contrib.checks.truncated_value import TruncatedValue


@pytest.mark.parametrize('value', [
    'a' * 255,
    32767,
    2147483647,
])
def test_truncated_values(value):
    cell = goodtables.cells.create_cell('value', value)
    errors = TruncatedValue().check_row([cell])
    assert len(errors) == 1
    assert errors[0].code == 'truncated-value'


@pytest.mark.parametrize('value', [
    'a' * 254,
    32766,
    2147483646,
])
def test_not_truncated_values(value):
    cell = goodtables.cells.create_cell('value', value)
    errors = TruncatedValue().check_row([cell])
    assert not errors


def test_check_truncated_value_with_dates():
    # There was a bug where we didn't catch the correct exception when calling
    # int(date)
    cell = goodtables.cells.create_cell(
        'date',
        datetime.datetime.now()
    )
    errors = TruncatedValue().check_row([cell])

    assert not errors
