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
from tests import base


class TestStructureProcessor(base.BaseTestCase):

    def test_standalone_ignore_empty_rows_false(self):

        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_ignore_empty_rows_false(self):

        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        validator = Pipeline(filepath, processors=('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_ignore_empty_rows_true(self):

        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(ignore_empty_rows=True)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_ignore_empty_rows_true(self):

        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        options = {'structure': {'ignore_empty_rows': True}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_ignore_duplicate_rows_false(self):

        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_ignore_duplicate_rows_false(self):

        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        validator = Pipeline(filepath, processors=('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_ignore_duplicate_rows_true(self):

        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
                ignore_duplicate_rows=True)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_ignore_duplicate_rows_true(self):

        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        options = {'structure': {'ignore_duplicate_rows': True}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_ignore_defective_rows_false(self):

        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_ignore_defective_rows_false(self):

        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        validator = Pipeline(filepath, processors=('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_ignore_defective_rows_true(self):

        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
                ignore_defective_rows=True)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_ignore_defective_rows_true(self):

        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        options = {'structure': {'ignore_defective_rows': True}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_ignore_duplicate_columns_false(self):

        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_ignore_duplicate_columns_false(self):

        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        validator = Pipeline(filepath, processors=('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_ignore_duplicate_columns_true(self):

        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
                ignore_duplicate_columns=True)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_ignore_duplicate_columns_true(self):

        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        options = {'structure': {'ignore_duplicate_columns': True}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_ignore_headerless_columns_false(self):

        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_ignore_headerless_columns_false(self):

        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        validator = Pipeline(filepath, processors=('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_ignore_headerless_columns_true(self):

        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
                ignore_headerless_columns=True)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_ignore_headerless_columns_true(self):

        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        options = {'structure': {'ignore_headerless_columns': True}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_custom_empty_strings(self):

        filepath = os.path.join(self.data_dir, 'empty_rows_custom.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(empty_strings=('-',))
            result, report, data = validator.run(stream)

            self.assertFalse(result)

    def test_pipeline_custom_empty_strings(self):

        filepath = os.path.join(self.data_dir, 'empty_rows_custom.csv')
        options = {'structure': {'empty_strings': ('-',)}}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertFalse(result)

    def test_standalone_fail_fast_true(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_structure_errors.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(fail_fast=True)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_fail_fast_true(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_structure_errors.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             fail_fast=True, options=options)
        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 1)

    def test_standalone_fail_fast_false(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_structure_errors.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor()
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 2)

    def test_pipeline_fail_fast_false(self):

        filepath = os.path.join(self.data_dir, 'fail_fast_two_structure_errors.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             options=options)
        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 2)

    # def test_standalone_transform_true(self):
    #     filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
    #     with io.open(filepath) as stream:
    #         validator = processors.StructureProcessor(
    #             ignore_headerless_columns=True)
    #         result, report, data = validator.run(stream)

    #         self.assertTrue(result)

    # def test_pipeline_transform_true(self):
    #     self.assertTrue(False)

    # def test_standalone_transform_false(self):
    #     filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
    #     with io.open(filepath) as stream:
    #         validator = processors.StructureProcessor(
    #             ignore_headerless_columns=True)
    #         result, report, data = validator.run(stream)

    #         self.assertTrue(result)

    # def test_pipeline_transform_false(self):
    #     self.assertTrue(False)

    def test_standalone_report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(report_limit=1)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 1)

    def test_pipeline_report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             report_limit=1, options=options)
        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 1)

    def test_standalone_report_limit_out_range(self):

        limit = processors.StructureProcessor.REPORT_LIMIT_MAX
        validator = processors.StructureProcessor(report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)

    def test_pipeline_report_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        limit = Pipeline.REPORT_LIMIT_MAX
        validator = Pipeline(filepath, report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)

    def test_standalone_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(row_limit=2)
            result, report, data = validator.run(stream)

            self.assertEqual(len(report.generate()['results']), 0)

    def test_pipeline_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             row_limit=2, options=options)
        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 0)

    def test_standalone_row_limit_out_range(self):

        limit = processors.StructureProcessor.ROW_LIMIT_MAX
        validator = processors.StructureProcessor(row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)

    def test_pipeline_row_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        limit = Pipeline.ROW_LIMIT_MAX
        validator = Pipeline(filepath, row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)
        self.assertEqual(validator.pipeline[0].row_limit, limit)

    def test_standalone_report_stream_valid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()))
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
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
        validator = Pipeline(filepath, processors=('structure',),
                             report_stream=report_stream, options=options)

        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 0)

        report_stream.seek(0)
        for line in report_stream:
            self.assertTrue(json.loads(line.rstrip('\n')))

    def test_standalone_report_stream_invalid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.BufferedReader(io.BytesIO())
        self.assertRaises(exceptions.ProcessorBuildError,
                          processors.StructureProcessor,
                          report_stream=report_stream)

    def test_pipeline_report_stream_invalid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        # stream is not writable
        report_stream = io.BufferedReader(io.BytesIO())
        options = {}
        args = [filepath]
        kwargs = {'report_stream': report_stream, 'options': options}

        self.assertRaises(exceptions.PipelineBuildError, Pipeline, *args, **kwargs)

    def test_standalone_report_stream_none(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = None
        with io.open(filepath) as stream:
            validator = processors.StructureProcessor(
                report_stream=report_stream)
            result, report, data = validator.run(stream)

            self.assertTrue(result)

    def test_pipeline_report_stream_none(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = None
        options = {}
        validator = Pipeline(filepath, processors=('structure',),
                             report_stream=report_stream, options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_standalone_empty_rows_are_not_duplicatable(self):

        filepath = os.path.join(self.data_dir, 'empty_rows_multiple.csv')
        validator = processors.StructureProcessor(fail_fast=False)
        result, report, data = validator.run(filepath)

        self.assertEqual(len(report.generate()['results']), 11)

    def test_pipeline_empty_rows_are_not_duplicatable(self):

        filepath = os.path.join(self.data_dir, 'empty_rows_multiple.csv')
        validator = Pipeline(filepath, processors=('structure',), fail_fast=False)
        result, report = validator.run()

        self.assertEqual(len(report.generate()['results']), 11)

    def test_processor_run_error_when_data_http_error(self):

        data_source = 'https://okfn.org/this-url-cant-possibly-exist-so-lets-test-404/'
        processor = processors.StructureProcessor()

        self.assertRaises(exceptions.ProcessorBuildError, processor.run, data_source)

    def test_processor_run_error_when_data_http_error(self):

        data_source = 'https://www.google.com/'
        processor = processors.StructureProcessor()

        self.assertRaises(exceptions.DataSourceIsHTMLError, processor.run, data_source)

    def test_processor_run_error_when_wrong_encoding(self):

        data_source = os.path.join(self.data_dir, 'hmt', 'BIS_spending_over__25_000_July_2014.csv')
        encoding = 'UTF-8'  # should be 'ISO-8859-2'
        processor = processors.StructureProcessor()

        self.assertRaises(exceptions.DataSourceDecodeError, processor.run,
                          data_source, encoding=encoding)
