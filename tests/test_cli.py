# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
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

    def tearDown(self):
        super(TestCLI, self).tearDown()

    def test_pipeline_from_url(self):

        c = ['python', 'goodtables/cli/main.py', 'pipeline',
             self.data_url]
        result = subprocess.check_output(c)

        self.assertEqual([], json.loads(result.decode('utf-8'))['results'])

    def test_pipeline_from_filepath(self):

        c = ['python', 'goodtables/cli/main.py', 'pipeline',
             self.data_filepath]
        result = subprocess.check_output(c)

        self.assertEqual([], json.loads(result.decode('utf-8'))['results'])

    def test_pipeline_with_schema(self):

        c = ['python', 'goodtables/cli/main.py', 'pipeline',
             self.data_filepath, '--schema', self.schema_filepath]
        result = subprocess.check_output(c)

        self.assertEqual([], json.loads(result.decode('utf-8'))['results'])

    def test_structure_from_filepath(self):

        c = ['python', 'goodtables/cli/main.py', 'structure',
             self.data_filepath, '--output', 'json']
        result = subprocess.check_output(c)

        self.assertTrue(result)

    def test_schema_from_filepath(self):

        c = ['python', 'goodtables/cli/main.py', 'schema',
             self.data_filepath, '--schema', self.schema_filepath, '--output', 'json']
        result = subprocess.check_output(c)

        self.assertTrue(result)
