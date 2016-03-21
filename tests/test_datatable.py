# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from goodtables import datatable
from goodtables import exceptions
from tests import base


class TestDataTable(base.BaseTestCase):

    def setUp(self):
        super(TestDataTable, self).setUp()

    def tearDown(self):
        super(TestDataTable, self).tearDown()

    def test_404_raises(self):

        data_source = 'https://okfn.org/this-url-cant-possibly-exist-so-lets-test-404/'

        self.assertRaises(exceptions.DataSourceHTTPError,
                          datatable.DataTable, data_source)

    def test_html_raises(self):

        data_source = 'https://www.google.com/'

        self.assertRaises(exceptions.DataSourceFormatUnsupportedError,
                          datatable.DataTable, data_source)


    def test_excel_from_file(self):

        data_source =  os.path.join(self.data_dir, 'hmt', 'BIS_monthly_spend_December_2012.xls')
        data = datatable.DataTable(data_source, format='excel')

        self.assertTrue(data.headers)

    def test_excel_from_url(self):

        data_source = 'https://github.com/okfn/goodtables/raw/master/examples/hmt/BIS_monthly_spend_December_2012.xls'
        data = datatable.DataTable(data_source, format='excel')

        self.assertTrue(data.headers)

    def test_wrong_encoding_raises(self):

        data_source = os.path.join(self.data_dir, 'hmt','BIS_spending_over__25_000_July_2014.csv')
        encoding = 'UTF-8'  # should be 'ISO-8859-2'
        self.assertRaises(exceptions.DataSourceDecodeError, datatable.DataTable,
                          data_source, encoding=encoding, decode_strategy=None)

    def test_wrong_encoding_replaces(self):

        data_source = os.path.join(self.data_dir, 'hmt','BIS_spending_over__25_000_July_2014.csv')
        encoding = 'UTF-8'  # should be 'ISO-8859-2'
        decode_strategy = 'replace'
        data = datatable.DataTable(data_source, encoding=encoding, decode_strategy=decode_strategy)

        self.assertTrue(data)

    def test_set_decoding_on_self_when_detected(self):

        data_source = os.path.join(self.data_dir, 'jungle','VilleMTP_MTP_BudgetPri_2015.csv')
        data = datatable.DataTable(data_source)
        self.assertEqual(data.encoding, 'windows-1252')

    def test_set_decoding_on_self_when_passed(self):

        data_source = os.path.join(self.data_dir, 'jungle','VilleMTP_MTP_BudgetPri_2015.csv')
        encoding = 'windows-1252'
        data = datatable.DataTable(data_source, encoding=encoding)
        self.assertEqual(data.encoding, data.passed_encoding)
