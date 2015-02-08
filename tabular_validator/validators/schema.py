# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base
from ..utilities import table_schema


class TableSchemaValidator(base.Validator):

    """Validate data against a JSON Table Schema."""

    name = 'tableschema'

    def __init__(self, fail_fast=False, transform=True, report_limit=1000,
                 table_schema_source=None, ignore_field_order=True, **kwargs):

        super(TableSchemaValidator, self).__init__(
            fail_fast=fail_fast, transform=transform,
            report_limit=report_limit)

        self.ignore_field_order = ignore_field_order
        self.table_schema_source = table_schema_source
        if not self.table_schema_source:
            self.schema = None
        else:
            self.schema = self.schema_model(self.table_schema_source)

    def schema_model(self, schema_source):
        return table_schema.JSONTableSchema(schema_source)

#    def pre_run(self, headers, values):
#        if self.schema is None:
#            # make a schema
#            # TODO: 50 here is arbitrary
#            sample_data = [row for row in values][:50]
#            guessed_schema = table_schema.make(headers, sample_data)
#            self.schema = self.schema_model(guessed_schema)
#
#        return True, headers, values

    def run_header(self, headers):

        valid = True

        if self.ignore_field_order:
            if not (set(headers) == set(self.schema.headers)):
                valid = False
                self.report.write({
                    'name': 'Incorrect·Header',
                    'category': 'headers',
                    'level': 'error',
                    'position': None,
                    'message': 'The headers do not match the schema'
                })

        else:
            if not (headers == self.schema.headers):
                valid = False
                self.report.write({
                    'name': 'Incorrect Headers',
                    'category': 'headers',
                    'level': 'error',
                    'position': None,
                    'message': 'The headers do not match the schema'
                })

        return valid, headers

    def run_row(self, headers, index, row):

        valid = True

        if not len(headers) == len(row):
            valid = False
            self.report.write({
                'name': 'Incorrect Dimensions',
                'category': 'row',
                'level': 'error',
                'position': index,
                'message': 'The row does not match the header dimensions.'
            })

        else:
            for k, v in zip(headers, row):
                # check type and format
                if not self.schema.cast(k, v):
                    valid = False
                    self.report.write({
                        'name': 'Incorrect type',
                        'category': 'row',
                        'level': 'error',
                        'position': index,
                        'message': ('The cell {0} is of the wrong '
                                    'type'.format(k))
                    })

                # TODO: Check format

                # CONSTRAINTS
                constraints = self.schema.get_constraints(k)
                if constraints:
                    # check constraints.required
                    if constraints.get('required') and not v:
                        valid = False
                        self.report.write({
                            'name': 'Missing required field',
                            'category': 'row',
                            'level': 'error',
                            'position': index,
                            'message': ('The cell {0} has no value, but '
                                        'is required'.format(k))
                        })

                # TODO: check constraints.unique

                # TODO: check constraints.min* and constraints.max*

        if self.transform:
            pass

        return valid, headers, index, row
