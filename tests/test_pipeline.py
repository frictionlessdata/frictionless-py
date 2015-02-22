# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
from tabular_validator.pipeline import Pipeline
from tabular_validator import exceptions
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

    def test_dry_run_true(self):

        pipeline = Pipeline(self.data_string, dry_run=True)
        self.assertTrue(pipeline.dry_run)

    def test_dry_run_false(self):

        pipeline = Pipeline(self.data_string, dry_run=False)
        self.assertFalse(pipeline.dry_run)

    def test_workspace_local_implicit(self):

        pipeline = Pipeline(self.data_string, dry_run=False)
        self.assertTrue(pipeline.workspace)

    # def test_workspace_local_explicit(self):
    #     pipeline = Pipeline(self.data_string, workspace='tmp', dry_run=False)
    #     self.assertTrue(pipeline.workspace)

    # def test_workspace_s3(self):
    #     self.assertTrue(False)

    # def test_workspace_none(self):
    #     self.assertTrue(False)

    # def test_transform_true(self):
    #     self.assertTrue(False)

    # def test_transform_false(self):
    #     self.assertTrue(False)

    def test__report_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, validators=('structure',),
                             report_limit=1, options=options)
        result, report = validator.run()

        self.assertEqual(len(report['structure']['results']), 1)

    def test__report_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'report_limit_structure.csv')
        limit = Pipeline.REPORT_LIMIT_MAX
        validator = Pipeline(filepath, report_limit=(limit + 1))

        self.assertEqual(validator.report_limit, limit)


    def test_row_limit_in_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        options = {}
        validator = Pipeline(filepath, validators=('structure',),
                             row_limit=3, options=options)
        result, report = validator.run()

        self.assertEqual(len(report['structure']['results']), 1)

    def test_row_limit_out_range(self):

        filepath = os.path.join(self.data_dir, 'row_limit_structure.csv')
        limit = Pipeline.ROW_LIMIT_MAX
        validator = Pipeline(filepath, row_limit=(limit + 1))

        self.assertEqual(validator.row_limit, limit)

    def test_report_stream_valid(self):

        filepath = os.path.join(self.data_dir, 'valid.csv')
        report_stream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()))
        options = {}
        validator = Pipeline(filepath, validators=('schema',),
                             report_stream=report_stream, options=options)

        result, report = validator.run()

        self.assertEqual(len(report['schema']['results']), 0)

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

    def test_init_workspace(self):

        pipeline = Pipeline(self.data_string, dry_run=False)

        self.assertTrue(os.path.exists(
            os.path.join(pipeline.workspace, 'source.csv')))
        self.assertTrue(os.path.exists(
            os.path.join(pipeline.workspace, 'transform.csv')))
        self.assertTrue(os.path.exists(
            os.path.join(pipeline.workspace, 'dialect.json')))

    def test_create_file(self):

        filepath = 'example.file'
        headers = ['first', 'second', 'three']
        row = '1,2,3\n'
        pipeline = Pipeline(self.data_string, dry_run=False)
        pipeline.create_file(row, filepath, headers=headers)

        self.assertTrue(os.path.exists(os.path.join(pipeline.workspace, filepath)))

    def test_rm_workspace(self):

        pipeline = Pipeline(self.data_string, dry_run=False)
        self.assertTrue(pipeline.workspace)
        pipeline.rm_workspace()

        self.assertFalse(os.path.exists(pipeline.workspace))

    def test_generate_report(self):

        pipeline = Pipeline(self.data_string, dry_run=False)
        self.assertEqual(len(pipeline.generate_report()), 1)

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

    # def test_run_valid_dry_run(self):
    #     self.assertTrue(False)

    # def test_run_invalid_dry_run(self):
    #     self.assertTrue(False)

    # def test_run_valid_transform(self):
    #     self.assertTrue(False)

    # def test_run_invalid_transform(self):
    #     self.assertTrue(False)
