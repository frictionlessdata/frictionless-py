# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
from goodtables.pipeline import Pipeline
from goodtables import exceptions
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):

        super(TestPipeline, self).setUp()
        self.data_filepath = os.path.join(self.data_dir, 'valid.csv')
        self.data_url = 'https://raw.githubusercontent.com/rgrp/dataset-gla/master/data/all.csv'
        self.data_string = """id,name,age\n234,John,37\n235,Jill,27\n"""
        self.data_stream = io.open(self.data_filepath)
        self.schema_valid = os.path.join(self.data_dir, 'schema_valid_simple.json')
        self.schema_invalid = os.path.join(self.data_dir, 'schema_invalid_empty.json')
        self.openfiles.append(self.data_stream)

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

    def test_register_processor_append(self):

        pipeline = Pipeline(self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)

        pipeline.register_processor('schema')
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_register_processor_insert(self):

        pipeline = Pipeline(self.data_string)
        self.assertEqual(len(pipeline.pipeline), 1)

        pipeline.register_processor('schema', position=0)
        self.assertEqual(len(pipeline.pipeline), 2)

    def test_resolve_processor(self):

        pipeline = Pipeline(self.data_string)
        val = pipeline.resolve_processor('structure')

        self.assertEqual(val.__name__, 'StructureProcessor')

    def test_raise_if_data_none(self):
        self.assertRaises(exceptions.PipelineBuildError, Pipeline, None)

    def test__report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             report_limit=1, options=options)
        result, report = validator.run()

        self.assertEqual(len([r for r in report.generate()['results'] if r['processor'] == 'structure']), 1)

    def test__report_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        limit = Pipeline.REPORT_LIMIT_MAX
        validator = Pipeline(filepath, report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)


    def test_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             row_limit=3, options=options)
        result, report = validator.run()

        self.assertEqual(len([r for r in report.generate()['results'] if r['processor'] == 'structure']), 1)

    def test_row_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        limit = Pipeline.ROW_LIMIT_MAX
        validator = Pipeline(filepath, row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)

    def test_report_stream_valid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()))
        options = {}
        validator = Pipeline(filepath, processors=('schema',),
                             report_stream=report_stream, options=options)

        result, report = validator.run()

        self.assertEqual(len([r for r in report.generate()['results'] if r['processor'] == 'schema']), 0)

        report_stream.seek(0)
        for line in report_stream:
            self.assertTrue(json.loads(line.rstrip('\n')))

    def test_report_stream_invalid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.BufferedReader(io.BytesIO())
        options = {}
        args = [filepath]
        kwargs = {'report_stream': report_stream, 'options': options}
        self.assertRaises(exceptions.PipelineBuildError, Pipeline, *args, **kwargs)

    def test_report_stream_none(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = None
        options = {}
        validator = Pipeline(filepath, report_stream=report_stream,
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    # def test_get_dialect_valid(self):
    #     self.assertTrue(False)

    # def test_get_dialect_invalid(self):
    #     self.assertTrue(False)

    # def test_get_dialect_none(self):
    #     self.assertTrue(False)

    # def test_get_pipeline_invalid(self):
    #     self.assertTrue(False)

    # def test_data_not_csv(self):
    #     self.assertTrue(False)

    def test_set_report_meta(self):

        pipeline = Pipeline(self.data_string)
        pipeline.set_report_meta()
        self.assertEqual(len(pipeline.report.generate()['meta']['headers']), 3)

    def test_header_index_valid(self):

        filepath = os.path.join(self.data_dir, 'valid_header_index_3.csv')
        options = {}
        validator = Pipeline(filepath, options=options, header_index=3)
        result, report = validator.run()

        self.assertTrue(result)

    def test_header_index_invalid(self):

        filepath = os.path.join(self.data_dir, 'invalid_header_index_1.csv')
        options = {}
        validator = Pipeline(filepath, options=options, header_index=1)
        result, report = validator.run()

        self.assertFalse(result)

    def test_report_summary(self):

        filepath = os.path.join(self.data_dir, 'invalid_header_index_1.csv')
        options = {}
        validator = Pipeline(filepath, options=options, header_index=1)
        result, report = validator.run()
        generated = report.generate()

        self.assertEqual(generated['meta']['bad_row_count'], 1)
        self.assertEqual(generated['meta']['row_count'], 9)

    def test_report_summary_incorrect_type(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_schema_errors.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',), options=options, fail_fast=True)
        result, report = validator.run()

        for col in report.generate()['meta']['columns']:
            if col['name'] == 'id':
                out = col['bad_type_percent']
                break

        self.assertEqual(out, 33)

    def test_pipeline_build_error_when_data_http_error(self):

        data_source = 'https://okfn.org/this-url-cant-possibly-exist-so-lets-test-404/'

        self.assertRaises(exceptions.DataSourceHTTPError, Pipeline, data_source)

    def test_pipeline_build_error_when_data_html_error(self):

        data_source = 'https://www.google.com/'

        self.assertRaises(exceptions.DataSourceIsHTMLError, Pipeline, data_source)

    def test_pipeline_build_error_when_wrong_encoding(self):

        data_source = os.path.join(self.data_dir, 'hmt','BIS_spending_over__25_000_July_2014.csv')
        encoding = 'UTF-8'  # should be 'ISO-8859-2'

        self.assertRaises(exceptions.DataSourceDecodeError, Pipeline, data_source,
                          encoding=encoding, decode_strategy=None)

    def test_bad_post_task_raises(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        say_hi = 'Say Hi!'
        self.assertRaises(exceptions.InvalidHandlerError, Pipeline,
                          filepath, post_task=say_hi)

    def test_bad_report_post_task_raises(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        say_hi = 'Say Hi!'
        self.assertRaises(exceptions.InvalidHandlerError, Pipeline,
                          filepath, report_post_task=say_hi)
