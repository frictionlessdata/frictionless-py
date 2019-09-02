# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from ...registry import check
from ...error import Error


# Module API

@check('foreign-keys', type='custom', context='body')
class ForeignKeys(object):

    def __init__(self, **options):
        pass

    def check_row(self, cells):
        pass
