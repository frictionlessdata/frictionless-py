# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from goodtables.pipeline import Pipeline
from goodtables import processors
from goodtables import exceptions
from tests import base


class TestJungle(base.BaseTestCase):

    """A selection of CSV fields from the wild."""

    def test_gla_source_clean(self):

        data = 'https://raw.githubusercontent.com/rgrp/dataset-gla/master/data/all.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_one(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-250-report-2013-14-P07.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_two(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-250-report-2014-15-P07.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_three(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-250-report-2014-15-P08.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_four(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-2011-12-P13-500.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_five(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-2012-13-P10-250.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_gla_source_six(self):

        data = os.path.join(self.data_dir, 'jungle', 'gla-december_2009.csv')
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertFalse(result)
        self.assertTrue(pipeline.data)

    def test_messytables_source_one(self):

        data = 'https://raw.githubusercontent.com/okfn/messytables/master/horror/spanish_chars.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_messytables_source_two(self):

        data = 'https://raw.githubusercontent.com/okfn/messytables/master/horror/utf-16le_encoded.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_messytables_source_three(self):

        data = 'https://raw.githubusercontent.com/okfn/messytables/master/horror/sparse_with_column_errors.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_messytables_source_four(self):

        data = 'https://raw.githubusercontent.com/okfn/messytables/master/horror/skip_initials.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_messytables_source_five(self):

        data = 'https://raw.githubusercontent.com/okfn/messytables/master/horror/characters.csv'
        pipeline = Pipeline(data)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_messytables_source_six(self):

        data = os.path.join(self.data_dir, 'jungle', 'messytables-excel_properties.xls')
        pipeline = Pipeline(data, format='excel')
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_multilingual_xlsx(self):

        data = os.path.join(self.data_dir, 'jungle', 'multilingual.xlsx')
        pipeline = Pipeline(data, format='excel')
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_hmt_bis_one(self):

        data = os.path.join(self.data_dir, 'hmt','BIS_spending_over__25_000_July_2014.csv')
        encoding = 'ISO-8859-2'
        pipeline = Pipeline(data, encoding=encoding)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_htm_bis_two(self):
        # excel
        data = os.path.join(self.data_dir, 'hmt','BIS_monthly_spend_December_2012.xls')
        pipeline = Pipeline(data, format='excel')
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_pipeline_hmt_bbsrc(self):

        data = os.path.join(self.data_dir, 'hmt','1011-bbsrc-25k-spend-return.csv')
        encoding = 'ISO-8859-2'
        pipeline = Pipeline(data, encoding=encoding)
        result, report = pipeline.run()

        self.assertTrue(pipeline.data)

    def test_standalone_hmt_bbsrc(self):

        data =  os.path.join(self.data_dir, 'hmt','1011-bbsrc-25k-spend-return.csv')
        encoding = 'ISO-8859-2'
        validator = processors.StructureProcessor()
        result, report, data = validator.run(data, encoding=None)

        self.assertTrue(data)
