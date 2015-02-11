# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
from tabular_validator import validators
from tabular_validator.pipeline import Pipeline
from tabular_validator.utilities import table_schema
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


class TestTableSchemaValidator(base.BaseTestCase):

    def test_in_standalone_schema_valid_simple(self):
        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = validators.SchemaValidator(schema=schema)
            result, report = validator.run(data_stream)

            self.assertTrue(result)

    def test_in_pipeline_schema_valid_simple(self):
        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_valid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema':{'schema': schema}}
            validator = Pipeline(validators=('schema',),
                                 data=data_filepath,
                                 options=options)
            result, report = validator.run()

            self.assertTrue(result)

    def test_in_standalone_schema_invalid_simple(self):
        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_invalid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            validator = validators.SchemaValidator(schema=schema)
            result, report = validator.run(data_stream)

            self.assertFalse(result)

    def test_in_pipeline_schema_invalid_simple(self):
        data_filepath = os.path.join(self.data_dir, 'contacts', 'people.csv')
        schema_filepath = os.path.join(self.data_dir, 'contacts',
                                       'schema_invalid.json')
        with io.open(data_filepath) as data_stream, \
                 io.open(schema_filepath) as schema_stream:
            schema = json.load(schema_stream)
            options = {'schema': {'schema': schema}}
            validator = Pipeline(validators=('structure', 'schema',),
                                 data=data_filepath,
                                 options=options)
            result, report = validator.run()

            self.assertFalse(result)
