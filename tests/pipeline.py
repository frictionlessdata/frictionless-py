import os
import io
from .base import BaseTestCase
from tabular_validator.pipeline import ValidationPipeline


class TestPipeline(BaseTestCase):

    def setUp(self):
        super(TestPipeline, self).setUp()
        self.data_filepath = os.path.join(self.data_dir, 'valid.csv')
        self.data_url = 'http://index.okfn.org/api/places.csv'
        self.data_string = """id,name,age\n234,John,37\n235,Jill,27"""
        self.data_stream = io.open(self.data_filepath)
        self.openfiles.append(self.data_stream)

    def tearDown(self):
        super(TestPipeline, self).tearDown()

    def test_from_stream(self):
        pipeline = ValidationPipeline(self.data_stream)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_filepath(self):
        pipeline = ValidationPipeline(self.data_filepath)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_url(self):
        pipeline = ValidationPipeline(self.data_url)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)

    def test_from_string(self):
        pipeline = ValidationPipeline(self.data_string)
        result, report = pipeline.run()
        self.assertTrue(pipeline.table)
