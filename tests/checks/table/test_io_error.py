# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import tabulator
from goodtables import checks


# Test

def test_io_error_good():
    exception = Exception()
    assert checks.io_error(exception) == []


def test_io_error_bad():
    exception = tabulator.exceptions.TabulatorException()
    assert checks.io_error(exception) == [
        {'message': 'IO error', 'row-number': None, 'column-number': None, },
    ]
