import os
import io
from tabular_validator import validators
from tabular_validator.pipeline import ValidationPipeline
from .base import BaseTestCase


class TestStructureValidator(BaseTestCase):

    def test_in_standalone_empty_rows(self):
        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator()
            result, report = validator.run(stream)

            self.assertFalse(result)

    def test_in_standalone_empty_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator(ignore_empty_rows=True)
            result, report = validator.run(stream)

            self.assertTrue(result)

    def test_in_standalone_duplicate_rows(self):
        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator()
            result, report = validator.run(stream)

            self.assertFalse(result)

    def test_in_standalone_duplicate_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator(
                ignore_duplicate_rows=True)
            result, report = validator.run(stream)

            self.assertTrue(result)

    def test_in_standalone_headerless_columns(self):
        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator()
            result, report = validator.run(stream)

            self.assertFalse(result)

    def test_in_standalone_headerless_columns_allowed(self):
        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator(
                ignore_headerless_columns=True)
            result, report = validator.run(stream)

            self.assertTrue(result)

    def test_in_standalone_duplicate_column_headers(self):
        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator()
            result, report = validator.run(stream)

            self.assertFalse(result)

    def test_in_standalone_duplicate_column_headers_allowed(self):
        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator(
                ignore_duplicate_column_headers=True)
            result, report = validator.run(stream)

            self.assertTrue(result)

    def test_in_standalone_defective_rows(self):
        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator()
            result, report = validator.run(stream)

            self.assertFalse(result)

    def test_in_standalone_defective_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        with io.open(filepath) as stream:
            validator = validators.StructureValidator(
                ignore_defective_rows=True)
            result, report = validator.run(stream)

            self.assertTrue(result)


class TestStructureValidatorPipeline(BaseTestCase):

    def test_in_pipeline_empty_rows(self):
        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        validator = ValidationPipeline(filepath, ('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_in_pipeline_empty_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'empty_rows.csv')
        options = {'structure': {'ignore_empty_rows': True}}
        validator = ValidationPipeline(filepath, ('structure',),
                                       options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_in_pipeline_duplicate_rows(self):
        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        validator = ValidationPipeline(filepath, ('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_in_pipeline_duplicate_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'duplicate_rows.csv')
        options = {'structure': {'ignore_duplicate_rows': True}}
        validator = ValidationPipeline(filepath, ('structure',),
                                       options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_in_pipeline_headerless_columns(self):
        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        validator = ValidationPipeline(filepath, ('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_in_pipeline_headerless_columns_allowed(self):
        filepath = os.path.join(self.data_dir, 'headerless_columns.csv')
        options = {'structure': {'ignore_headerless_columns': True}}
        validator = ValidationPipeline(filepath, ('structure',),
                                       options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_in_pipeline_duplicate_column_headers(self):
        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        validator = ValidationPipeline(filepath, ('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_in_pipeline_duplicate_column_headers_allowed(self):
        filepath = os.path.join(self.data_dir, 'duplicate_columns.csv')
        options = {'structure': {'ignore_duplicate_column_headers': True}}
        validator = ValidationPipeline(filepath, ('structure',),
                                       options=options)
        result, report = validator.run()

        self.assertTrue(result)

    def test_in_pipeline_defective_rows(self):
        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        validator = ValidationPipeline(filepath, ('structure',))
        result, report = validator.run()

        self.assertFalse(result)

    def test_in_pipeline_defective_rows_allowed(self):
        filepath = os.path.join(self.data_dir, 'defective_rows.csv')
        options = {'structure': {'ignore_defective_rows': True}}
        validator = ValidationPipeline(filepath, ('structure',),
                                       options=options)
        result, report = validator.run()

        self.assertTrue(result)
