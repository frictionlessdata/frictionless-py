# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import subprocess
from goodtables import utilities
from tests import base


class TestUtilities(base.BaseTestCase):

    def setUp(self):

        super(TestUtilities, self).setUp()

    def test_get_report_result_types(self):
        self.assertTrue(utilities.helpers.get_report_result_types())
