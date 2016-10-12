# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest


@pytest.fixture(scope='session')
def log():
    def fixture(struct):
        """Pack report/errors to (row-number, column-number, code) tuples list.
        """
        result = []
        if isinstance(struct, list):
            for error in struct:
                result.append((
                    error['row-number'],
                    error['column-number'],
                    error['code']))
        return result
    return fixture
