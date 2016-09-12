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

    def test_make_valid_composed_url(self):
        url = ('http://webarchive.nationalarchives.gov.uk/+/'
               'http://www.nio.gov.uk/transaction_spend_data_august_10_northern_ireland_office.xls')
        assertion = '+' in utilities.helpers.make_valid_url(url)
        self.assertTrue(assertion)

    def test_make_valid_url(self):
        url = ('http://goodtables.okfnlabs.org/reports?'
              'data_url=http://data.defra.gov.uk/ops/government_procurement_card/over_£500_GPC_apr_2013.csv')
        assertion = '£' not in utilities.helpers.make_valid_url(url)
        self.assertTrue(assertion)

    def test_make_valid_url_dont_break_query(self):
        url = 'http://next.openspending.org/fdp-adapter/convert?url=https%3A%2F%2Fraw.githubusercontent.com%2Fkravets-levko%2Fdata%2Fmaster%2Ftest.xlsx.csv'
        self.assertEqual(utilities.helpers.make_valid_url(url), url)
