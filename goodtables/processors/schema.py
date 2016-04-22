# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsontableschema
from . import base
import copy

RESULTS = {
    'schema_001': {
        'id': 'schema_001',
        'name': 'Incorrect Headers',
        'msg': {
            'missing': 'Missing required column headings: {0}.',
            'misplaced': ('Misplaced column headings: {0}. Please respect the order'
                          ' set by the schema or change \"ignore_field_order\" to true.')
        },
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
        'msg': 'The value \"{0}\" in column \"{1}\" is not a valid {2}.',
        'help': '',
        'help_edit': ''
    },
    'schema_004': {
        'id': 'schema_004',
        'name': 'Required Field',
        'msg': 'Column \"{0}\" is a required field, but it contains no value.',
        'help': '',
        'help_edit': ''
    },
    'schema_005': {
        'id': 'schema_005',
        'name': 'Non-Required Field (Empty/Null)',
        'msg': 'Column \"{0}\" is a non-required field, and has a null value.',
        'help': '',
        'help_edit': ''
    },
    'schema_006': {
        'id': 'schema_006',
        'name': 'Unique Field',
        'msg': 'Column \"{0}\" is a unique field, yet the value \"{1}\" already exists.',
        'help': '',
        'help_edit': ''
    },
    'schema_007': {
        'id': 'schema_007',
        'name': 'Incorrect Type Extra Field',
        'msg': ('Column \"{0}\" is an extra field.'
                'However, the value \"{1}\" is not a valid {2}.'),
        'help': '',
        'help_edit': ''
    },
    'schema_008': {
        'id': 'schema_008',
        'name': 'Extra Field (Empty/Null)',
        'msg': 'Column \"{0}\" is an extra field and it has a null value.',
        'help': '',
        'help_edit': ''
    }
}


class SchemaProcessor(base.Processor):

    """Process data against a JSON Table Schema."""

    name = 'schema'
    RESULT_TYPES = RESULTS


    def __init__(self, fail_fast=False, report_limit=1000,
                 row_limit=30000, schema=None, ignore_field_order=True,
                 report_stream=None, report=None, result_level='error',
                 infer_schema=False, process_extra_fields=False,
                 case_insensitive_headers=False, **kwargs):

        super(SchemaProcessor, self).__init__(
            fail_fast=fail_fast, report_limit=report_limit,
            row_limit=row_limit, report_stream=report_stream, report=report,
            result_level=result_level)

        self.infer_schema = infer_schema
        self.case_insensitive_headers = case_insensitive_headers
        self.ignore_field_order = ignore_field_order
        self.process_extra_fields = process_extra_fields

        if not schema:
            self.schema = None
        else:
            self.schema = self.schema_model(schema)

        self._uniques = {}

    def schema_model(self, schema):
        try:
            model = jsontableschema.model.SchemaModel(schema, self.case_insensitive_headers)
        except (jsontableschema.exceptions.InvalidJSONError, jsontableschema.exceptions.InvalidSchemaError) as e:
            raise e

        return model

    def pre_run(self, data_table):

        sample_values = data_table.get_sample(300)

        if (self.schema is None) and self.infer_schema:
            self.schema = self.schema_model(jsontableschema.infer(data_table.headers, sample_values))

        if self.schema and self.process_extra_fields:
            self.extra_fields = (set(data_table.headers)).difference(set(self.schema.headers))
            infered_schema = jsontableschema.infer(data_table.headers, sample_values)
            complete_schema_dict = self.schema._to_python()

            for field in infered_schema['fields']:
                if field['name'] in self.extra_fields:
                    complete_schema_dict['fields'].append(copy.deepcopy(field))

            self.schema = self.schema_model(complete_schema_dict)

        return True, data_table

    def run_header(self, headers, header_index=0):

        valid = True

        if self.case_insensitive_headers:
            headers = [name.lower() for name in headers]

        if self.schema:
            required_headers = self.schema.required_headers
            required_headers_set = set(required_headers)
            headers_set = set(headers)

            if self.ignore_field_order:
                if not headers_set.issuperset(required_headers_set):
                    missing_set = required_headers_set.difference(headers_set)
                    valid = False
                    _type = RESULTS['schema_001']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg']['missing'].format(', '.join(missing_set)),
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
                req_headers_len = len(required_headers)
                target_headers = headers[:req_headers_len]

                if not (target_headers == required_headers):
                    missing_set = required_headers_set.difference(headers_set)
                    misplaced_set = [th for th, rh in zip(target_headers, required_headers)
                                     if th != rh]
                    valid = False
                    _type = RESULTS['schema_001']
                    msg = lambda set, key: _type['msg'][key].format(', '.join(set)) if set else ''
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        ' '.join([msg(missing_set, 'missing'),
                                 msg(misplaced_set, 'misplaced')]),
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
                        # CONSTRAINTS
                        constraints = self.schema.get_constraints(column_name)

                        if constraints is not None and \
                           constraints.get('required', False) is True and \
                           (column_value in self.schema.NULL_VALUES):

                            valid = False
                            _type = RESULTS['schema_004']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_ERROR,
                                _type['msg'].format(column_name),
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

                        if constraints is not None and \
                           constraints.get('required', False) is False and \
                           (column_value in self.schema.NULL_VALUES) and \
                           self.result_level == self.RESULT_LEVEL_INFO:
                            # add info result
                            _type = RESULTS['schema_005']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_INFO,
                                _type['msg'].format(column_name),
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

                        if self.process_extra_fields and \
                           column_name in self.extra_fields and \
                           column_value in self.schema.NULL_VALUES and \
                           self.result_level == self.RESULT_LEVEL_INFO:

                            _type = RESULTS['schema_008']
                            entry = self.make_entry(
                                self.name,
                                self.RESULT_CATEGORY_ROW,
                                self.RESULT_LEVEL_INFO,
                                _type['msg'].format(column_name),
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

                        if constraints is not None and \
                            constraints.get('unique') is True:

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
                        # check type and format
                        try:
                            schema_cast = self.schema.cast(column_name,
                                                           column_value)
                        except (jsontableschema.exceptions.InvalidCastError,
                                jsontableschema.exceptions.ConstraintError):
                            schema_cast = False

                        if schema_cast is False:
                            expected_type = self.schema.get_type(column_name).name.title()

                            if self.process_extra_fields and \
                               column_name in self.extra_fields and \
                               self.result_level == self.RESULT_LEVEL_INFO:

                                _type = RESULTS['schema_007']
                                entry = self.make_entry(
                                    self.name,
                                    self.RESULT_CATEGORY_ROW,
                                    self.RESULT_LEVEL_INFO,
                                    _type['msg'].format(column_name, column_value,
                                                        expected_type),
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

                                valid = False
                                _type = RESULTS['schema_003']
                                entry = self.make_entry(
                                    self.name,
                                    self.RESULT_CATEGORY_ROW,
                                    self.RESULT_LEVEL_ERROR,
                                    _type['msg'].format(column_value, column_name,
                                                        expected_type),
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

        return valid, headers, index, row
