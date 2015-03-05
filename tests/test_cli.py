# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import subprocess
from goodtables.pipeline import Pipeline
from goodtables import exceptions
from goodtables import compat
from tests import base


class TestCLI(base.BaseTestCase):

    def setUp(self):

        super(TestCLI, self).setUp()
        self.data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        self.schema_filepath = os.path.join(self.data_dir, 'contacts', 'schema_valid.json')
        self.data_url = 'https://raw.githubusercontent.com/rgrp/dataset-gla/master/data/all.csv'
        self.data_string = """id,name,age\n234,John,37\n235,Jill,27\n"""
        self.successmsg = compat.to_bytes('The data source is valid')
        self.failmsg = compat.to_bytes('The data source is invalid')

    def tearDown(self):
        super(TestCLI, self).tearDown()

    def test_from_url(self):

        c = ['python', 'goodtables/cli/main.py', 'validate',
             self.data_url]
        result = subprocess.check_output(c)

        self.assertIn(self.successmsg, result)

    def test_from_filepath(self):

        c = ['python', 'goodtables/cli/main.py', 'validate',
             self.data_filepath]
        result = subprocess.check_output(c)

        self.assertIn(self.successmsg, result)

    def test_with_schema(self):

        c = ['python', 'goodtables/cli/main.py', 'validate',
             self.data_filepath, '--schema', self.schema_filepath]
        result = subprocess.check_output(c)

        self.assertIn(self.successmsg, result)

    # def test_from_url(self):

    #     pipeline = Pipeline(self.data_filepath)
    #     result, report = pipeline.run()

    #     self.assertTrue(pipeline.data)

    # def test_from_string(self):

    #     pipeline = Pipeline(self.data_url)
    #     result, report = pipeline.run()

    #     self.assertTrue(pipeline.data)
