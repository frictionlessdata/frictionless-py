# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jtskit
from . import base
from .. import exceptions


RESULTS = {
    'schema_001': {
        'id': 'schema_001',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema. Data has {0}, but they should be {1}.',
        'help': '',
        'help_edit': ''
    },
    'schema_002': {
        'id': 'schema_002',
        'name': 'Incorrect Dimensions',
        'msg': 'The row dimensions do not match the header dimensions.',
        'help': '',
        'help_edit': ''
    },
    'schema_003': {
        'id': 'schema_003',
        'name': 'Incorrect Type',
        'msg': 'The value is not a valid {0}.',
        'help': '',
        'help_edit': ''
    },
    'schema_004': {
        'id': 'schema_004',
        'name': 'Required Field',
        'msg': 'Column {0} is a required field, but no value can be found in row {1}.',
        'help': '',
        'help_edit': ''
    },
    'schema_005': {
        'id': 'schema_005',
        'name': 'Non-Required Field (Empty/Null)',
        'msg': 'Column {0} is a non-required field, and has a null value in row {1}.',
        'help': '',
        'help_edit': ''
    },
    'schema_006': {
        'id': 'schema_006',
        'name': 'Unique Field',
        'msg': 'Column {0} is a unique field, yet the value {1} already exists.',
        'help': '',
        'help_edit': ''
    }
}


class SchemaProcessor(base.Processor):

    """Process data against a JSON Table Schema."""

    name = 'schema'
    RESULT_TYPES = RESULTS

    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 row_limit=30000, schema=None, ignore_field_order=True,
                 report_stream=None, report=None,
                 result_level='error', infer_schema=False,
                 case_insensitive_headers=False, **kwargs):

        super(SchemaProcessor, self).__init__(
            fail_fast=fail_fast, transform=transform,
            report_limit=report_limit, row_limit=row_limit,
            report_stream=report_stream, report=report, result_level=result_level)

        self.infer_schema = infer_schema
        self.case_insensitive_headers = case_insensitive_headers
        self.ignore_field_order = ignore_field_order
        if not schema:
            self.schema = None
        else:
            self.schema = self.schema_model(schema)

        self._uniques = {}

    def schema_model(self, schema):
        try:
            model = jtskit.models.SchemaModel(schema, self.case_insensitive_headers)
        except (jtskit.exceptions.InvalidJSONError, jtskit.exceptions.InvalidSchemaError) as e:
            raise exceptions.ProcessorBuildError(e.msg)

        return model

    def pre_run(self, data_table):

        if (self.schema is None) and self.infer_schema:
            sample_values = data_table.get_sample(300)
            self.schema = self.schema_model(jtskit.infer(data_table.headers, sample_values))

        return True, data_table

    def run_header(self, headers, header_index=0):

        valid = True

        if self.case_insensitive_headers:
            headers = [name.lower() for name in headers]

        if self.schema:
            if self.ignore_field_order:
                if not (set(headers).issuperset(set(self.schema.required_headers))):

                    valid = False
                    _type = RESULTS['schema_001']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(headers, self.schema.headers),
                        _type['id'],
                        _type['name'],
                        headers,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

            else:
                header_length = len(headers)
                if not (headers == self.schema.required_headers[:header_length]):

                    valid = False
                    _type = RESULTS['schema_001']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(headers, self.schema.headers),
                        _type['id'],
                        _type['name'],
                        headers,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME,
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

        return valid, headers

    def run_row(self, headers, index, row):

        valid = True
        row_name = self.get_row_id(headers, row)

        if self.schema:
            if not (len(headers) == len(row)):

                valid = False
                _type = RESULTS['schema_002']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'],
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name,
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

            else:
                for column_name, column_value in zip(headers, row):

                    # handle case where column_name not even in schema
                    if not self.schema.has_field(column_name):
                        pass

                    # we know the field is in the schema
                    else:
                        # check type and format
                        if self.schema.cast(column_name, column_value) is False:

                            valid = False
                            _type = RESULTS['schema_003']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_ERROR,
                                _type['msg'].format(self.schema.get_type(column_name).name.title()),
                                _type['id'],
                                _type['name'],
                                row,
                                index,
                                row_name,
                                headers.index(column_name),
                                column_name
                            )

                            self.report.write(entry)
                            if self.fail_fast:
                                return valid, headers, index, row

                        # CONSTRAINTS
                        constraints = self.schema.get_constraints(column_name)

                        if constraints['required'] is True and \
                           (column_value in self.schema.NULL_VALUES):

                            valid = False
                            _type = RESULTS['schema_004']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_ERROR,
                                _type['msg'].format(column_name, index),
                                _type['id'],
                                _type['name'],
                                row,
                                index,
                                row_name,
                                headers.index(column_name),
                                column_name
                            )

                            self.report.write(entry)
                            if self.fail_fast:
                                return valid, headers, index, row

                        if constraints['required'] is False and \
                           (column_value in self.schema.NULL_VALUES) and \
                           self.result_level == self.RESULT_LEVEL_INFO:
                            # add info result
                            _type = RESULTS['schema_005']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_INFO,
                                _type['msg'].format(column_name, index),
                                _type['id'],
                                _type['name'],
                                row,
                                index,
                                row_name,
                                headers.index(column_name),
                                column_name
                            )

                            self.report.write(entry)
                            if self.fail_fast:
                                return valid, headers, index, row

                        if constraints.get('unique') is True:

                            if not self._uniques.get(column_name):
                                self._uniques[column_name] = set([column_value])

                            elif column_value in self._uniques[column_name]:
                                _type = RESULTS['schema_006']
                                entry = self.make_entry(
                                    self.name,
                                    self.RESULT_CATEGORY_ROW,
                                    self.RESULT_LEVEL_ERROR,
                                    _type['msg'].format(column_name, column_value),
                                    _type['id'],
                                    _type['name'],
                                    row,
                                    index,
                                    row_name,
                                    headers.index(column_name),
                                    column_name
                                )

                                self.report.write(entry)
                                if self.fail_fast:
                                    return valid, headers, index, row

                            else:
                                self._uniques[column_name].add(column_value)

                        # TODO: check constraints.min* and constraints.max*

        return valid, headers, index, row
