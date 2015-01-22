# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from tabular_validator.pipeline import ValidationPipeline
from tabular_validator import exceptions
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):
        super(TestPipeline, self).setUp()
        self.data_filepath = os.path.join(self.data_dir, 'valid.csv')
        self.data_url = 'http://index.okfn.org/api/places.csv'
        self.data_string = """id,name,age\n234,John,37\n235,Jill,27"""
        self.data_stream = io.open(self.data_filepath)
        self.schema_valid = os.path.join(self.data_dir, 'schema_valid.json')
        self.schema_invalid = os.path.join(self.data_dir, 'schema_invalid.json')
        self.openfiles.extend([
            self.data_stream
        ])

    def tearDown(self):
        super(TestPipeline, self).tearDown()

    def test_from_stream(self):
        pipeline = ValidationPipeline(data_source=self.data_stream)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_filepath(self):
        pipeline = ValidationPipeline(data_source=self.data_filepath)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_url(self):
        pipeline = ValidationPipeline(data_source=self.data_url)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_string(self):
        pipeline = ValidationPipeline(data_source=self.data_string)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_register_validator_append(self):
        pipeline = ValidationPipeline(data_source=self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)
        pipeline.register_validator('spec')
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_register_validator_insert(self):
        pipeline = ValidationPipeline(data_source=self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)
        pipeline.register_validator('spec', position=0)
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_resolve_validator(self):
        pipeline = ValidationPipeline(data_source=self.data_string)
        val = pipeline.resolve_validator('structure')
        self.assertEqual(val.__name__, 'StructureValidator')

    def test_validate_spec_valid(self):
        pipeline = ValidationPipeline(data_source=self.data_string,
                                      table_schema=self.schema_valid)
        self.assertTrue(pipeline)

    def test_validate_spec_invalid(self):
        self.assertRaises(exceptions.InvalidSpec, ValidationPipeline,
                          data_source=self.data_string,
                          table_schema=self.schema_invalid)
