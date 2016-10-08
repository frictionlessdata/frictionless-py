# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ....registry import check


# Module API

@check('maximum-length-constraint')
def maximum_length_constraint(row_number, columns, state=None):
    return []
