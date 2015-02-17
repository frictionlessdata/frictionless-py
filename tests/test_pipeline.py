# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from tabular_validator.pipeline import Pipeline
from tabular_validator import exceptions
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):
        super(TestPipeline, self).setUp()
        self.data_filepath = os.path.join(self.data_dir, 'valid.csv')
        self.data_url = 'http://index.okfn.org/api/places.csv'
        self.data_string = """id,name,age\n234,John,37\n235,Jill,27"""
        self.data_stream = io.open(self.data_filepath)
        self.schema_valid = os.path.join(self.data_dir, 'schema_valid_simple.json')
        self.schema_invalid = os.path.join(self.data_dir, 'schema_invalid_empty.json')
        self.openfiles.extend([
            self.data_stream
        ])

    def tearDown(self):
        super(TestPipeline, self).tearDown()

    def test_from_stream(self):
        pipeline = Pipeline(self.data_stream)
        result, report = pipeline.run()
        self.assertTrue(pipeline.data)

    def test_from_filepath(self):
        pipeline = Pipeline(self.data_filepath)
        result, report = pipeline.run()
        self.assertTrue(pipeline.data)

    def test_from_url(self):
        pipeline = Pipeline(self.data_url)
        result, report = pipeline.run()
        self.assertTrue(pipeline.data)

    def test_from_string(self):
        pipeline = Pipeline(self.data_string)
        result, report = pipeline.run()
        self.assertTrue(pipeline.data)

    def test_register_validator_append(self):
        pipeline = Pipeline(self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)
        pipeline.register_validator('schema')
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_register_validator_insert(self):
        pipeline = Pipeline(self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)
        pipeline.register_validator('schema', position=0)
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_resolve_validator(self):
        pipeline = Pipeline(self.data_string)
        val = pipeline.resolve_validator('structure')
        self.assertEqual(val.__name__, 'StructureValidator')

    def test_raise_if_data_none(self):
        self.assertRaises(exceptions.PipelineBuildError, Pipeline, None)
