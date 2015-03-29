# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
from goodtables import processors
from goodtables import exceptions
from goodtables.pipeline import Pipeline
from goodtables.utilities import table_schema
from tests import base


class TestValidateSchema(base.BaseTestCase):

    def test_schema_valid_simple(self):
        filepath = os.path.join(self.data_dir, 'schema_valid_simple.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertTrue(valid)

    def test_schema_valid_full(self):
        filepath = os.path.join(self.data_dir, 'schema_valid_full.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertTrue(valid)

    def test_schema_valid_pk_string(self):
        filepath = os.path.join(self.data_dir, 'schema_valid_pk_string.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertTrue(valid)

    def test_schema_valid_pk_array(self):
        filepath = os.path.join(self.data_dir, 'schema_valid_pk_array.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertTrue(valid)

    def test_schema_invalid_empty(self):
        filepath = os.path.join(self.data_dir, 'schema_invalid_empty.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertFalse(valid)

    def test_schema_invalid_wrong_type(self):
        filepath = os.path.join(self.data_dir, 'schema_invalid_wrong_type.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertFalse(valid)

    def test_schema_invalid_pk_string(self):
        filepath = os.path.join(self.data_dir, 'schema_invalid_pk_string.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertFalse(valid)

    def test_schema_invalid_pk_array(self):
        filepath = os.path.join(self.data_dir, 'schema_invalid_pk_array.json')
        with io.open(filepath) as stream:
            schema = json.load(stream)
        valid, report = table_schema.validate(schema)

        self.assertFalse(valid)


class TestSchemaProcessor(base.BaseTestCase):

    def test_standalone_schema_valid_simple(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = processors.SchemaProcessor(schema=schema)
            result, report, data = validator.run(data_stream)

            self.assertTrue(result)

    def test_pipeline_schema_valid_simple(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema':{'schema': schema}}
            validator = Pipeline(data_filepath,
                                 processors=('schema',),
                                 options=options)

            result, report = validator.run()

            self.assertTrue(result)

    def test_standalone_schema_invalid_simple(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_invalid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = processors.SchemaProcessor(schema=schema)
            result, report, data = validator.run(data_stream)

            self.assertFalse(result)

    def test_pipeline_schema_invalid_simple(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_invalid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema': {'schema': schema}}
            validator = Pipeline(data_filepath,
                                 processors=('structure', 'schema',),
                                 options=options)
            result, report = validator.run()

            self.assertFalse(result)

    def test_standalone_ignore_field_order_true(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid_not_field_order.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = processors.SchemaProcessor(schema=schema)
            result, report, data = validator.run(data_stream)

            self.assertTrue(result)

    def test_pipeline_ignore_field_order_true(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid_not_field_order.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema':{'schema': schema}}
            validator = Pipeline(data_filepath,
                                 processors=('schema',),
                                 options=options)
            result, report = validator.run()

            self.assertTrue(result)

    def test_standalone_ignore_field_order_false(self):
        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid_not_field_order.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = processors.SchemaProcessor(schema=schema,
                                                   ignore_field_order=False)
            result, report, data = validator.run(data_stream)

            self.assertFalse(result)

    def test_pipeline_ignore_field_order_false(self):

        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid_not_field_order.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema':{'schema': schema, 'ignore_field_order': False}}
            validator = Pipeline(data_filepath,
                                 processors=('schema',),
                                 options=options)
            result, report = validator.run()

            self.assertFalse(result)

    def test_standalone_fail_fast_true(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_schema_errors.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(fail_fast=True, schema=schema)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_fail_fast_true(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_schema_errors.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',),
                             fail_fast=True, options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 1)

    def test_standalone_fail_fast_false(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_schema_errors.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(schema=schema)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 7)

    def test_pipeline_fail_fast_false(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_schema_errors.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',),
                             options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 7)

    # def test_standalone_transform_true(self):
    #     self.assertTrue(False)

    # def test_pipeline_transform_true(self):
    #     self.assertTrue(False)

    # def test_standalone_transform_false(self):
    #     self.assertTrue(False)

    # def test_pipeline_transform_false(self):
    #     self.assertTrue(False)

    def test_standalone_report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_schema.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(report_limit=1, schema=schema)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_schema.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',),
                             report_limit=1, options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 1)
        self.assertEqual(validator.report_limit, 1)
        self.assertEqual(validator.pipeline[0].report_limit, 1)

    def test_standalone_report_limit_out_range(self):

        limit = processors.SchemaProcessor.REPORT_LIMIT_MAX
        validator = processors.SchemaProcessor(report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)

    def test_pipeline_report_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        limit = Pipeline.REPORT_LIMIT_MAX
        validator = Pipeline(filepath, processors=('schema',), report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)
        self.assertEqual(validator.pipeline[0].report_limit, limit)

    def test_standalone_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_schema.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(row_limit=2, schema=schema)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 0)

    def test_pipeline_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_schema.csv')
        schema = os.path.join(self.data_dir, 'test_schema.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',),
                             row_limit=2, options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 0)
        self.assertEqual(validator.row_limit, 2)
        self.assertEqual(validator.pipeline[0].row_limit, 2)

    def test_standalone_row_limit_out_range(self):

        limit = processors.SchemaProcessor.ROW_LIMIT_MAX
        validator = processors.SchemaProcessor(row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)

    def test_pipeline_row_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        limit = Pipeline.ROW_LIMIT_MAX
        validator = Pipeline(filepath, processors=('schema',), row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)
        self.assertEqual(validator.pipeline[0].row_limit, limit)

    def test_standalone_report_stream_valid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()))
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(
                report_stream=report_stream)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 0)

            report_stream.seek(0)
            for line in report_stream:
                self.assertTrue(json.loads(line.rstrip('\n')))

    def test_pipeline_report_stream_valid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()))
        options = {}
        validator = Pipeline(filepath, processors=('schema',),
                             report_stream=report_stream, options=options)

        result, report = validator.run()

        self.assertEqual(len(report['results']), 0)

        report_stream.seek(0)
        for line in report_stream:
            self.assertTrue(json.loads(line.rstrip('\n')))

    def test_standalone_report_stream_invalid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.BufferedReader(io.BytesIO())
        self.assertRaises(exceptions.ProcessorBuildError,
                          processors.SchemaProcessor,
                          report_stream=report_stream)

    def test_pipeline_report_stream_invalid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.BufferedReader(io.BytesIO())
        options = {}
        args = [filepath]
        kwargs = {'report_stream': report_stream, 'processors': ('schema',), 'options': options}
        self.assertRaises(exceptions.PipelineBuildError, Pipeline, *args, **kwargs)

    def test_standalone_report_stream_none(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = None
        with io.open(filepath) as stream:
            validator = processors.SchemaProcessor(
                report_stream=report_stream)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_report_stream_none(self):
        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = None
        options = {}
        validator = Pipeline(filepath, processors=('schema',),
                             report_stream=report_stream, options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_info_result_for_required_false(self):
        filepath = os.path.join(self.data_dir, 'required_false.csv')
        schema = os.path.join(self.data_dir, 'required_false_schema.json')
        validator = processors.SchemaProcessor(schema=schema, result_level='info')
        result, report, data = validator.run(filepath)

        self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_info_result_for_required_false(self):
        filepath = os.path.join(self.data_dir, 'required_false.csv')
        schema = os.path.join(self.data_dir, 'required_false_schema.json')
        options = {'schema': {'schema': schema, 'result_level': 'info'}}
        validator = Pipeline(filepath, processors=('schema',), options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 1)

    def test_standalone_infer_schema(self):
        filepath = os.path.join(self.data_dir, 'valid.csv')
        validator = processors.SchemaProcessor(infer_schema=True)
        result, report, data = validator.run(filepath)

        self.assertEqual(len(report.generate()['results']), 0)

    def test_pipeline_infer_schema(self):
        filepath = os.path.join(self.data_dir, 'valid.csv')
        options = {'schema': {'infer_schema': True}}
        validator = Pipeline(filepath, processors=('schema',), options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 0)

    def test_processor_run_error_when_data_http_error(self):

        data_source = 'https://okfn.org/this-url-cant-possibly-exist-so-lets-test-404/'
        processor = processors.SchemaProcessor()

        self.assertRaises(exceptions.ProcessorBuildError, processor.run, data_source)

    def test_processor_run_error_when_data_html_error(self):

        data_source = 'https://www.google.com/'
        processor = processors.SchemaProcessor()

        self.assertRaises(exceptions.ProcessorBuildError, processor.run, data_source)

    def test_processor_run_error_when_wrong_encoding(self):

        data_source = os.path.join(self.data_dir, 'hmt','BIS_spending_over__25_000_July_2014.csv')
        encoding = 'UTF-8'  # should be 'ISO-8859-2'
        processor = processors.SchemaProcessor()

        self.assertRaises(exceptions.ProcessorBuildError, processor.run,
                          data_source, encoding=encoding)

    def test_standalone_field_unique(self):
        filepath = os.path.join(self.data_dir, 'unique_field.csv')
        schema = os.path.join(self.data_dir, 'unique_field.json')
        validator = processors.SchemaProcessor(schema=schema)
        result, report, data = validator.run(filepath)

        self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_field_unique(self):
        filepath = os.path.join(self.data_dir, 'unique_field.csv')
        schema = os.path.join(self.data_dir, 'unique_field.json')
        options = {'schema': {'schema': schema}}
        validator = Pipeline(filepath, processors=('schema',), options=options)
        result, report = validator.run()

        self.assertEqual(len(report['results']), 1)
