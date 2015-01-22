# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base
from .. import utilities


class SchemaValidator(base.Validator):

    name = 'schema'

    def __init__(self, fail_fast=False, transform=True, report_limit=1000,
                 table_schema=None, ignore_file_order=True, **kwargs):

        super(SchemaValidator, self).__init__(fail_fast=fail_fast,
                                              transform=True,
                                              report_limit=1000)
        self.ignore_field_order = ignore_field_order
        self.table_schema = table_schema
        self.schema = self.schema_model(self.table_schema)

    def schema_model(self, schema_source):
        return JSONTableSchema(schema_source)

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
                    'message': 'The data fields do not match the schema'
                })

        else:
            if not (headers == self.schema.headers):
                valid = False
                self.report.write({
                    'name': 'Incorrect Headers',
                    'category': 'headers',
                    'level': 'error',
                    'position': None,
                    'message': ''
                })

        return valid, headers

    def run_row(self, headers, index, row):

        valid = True

        # NOT YET safe if headers repeat - need to build dict differently
        if not len(headers) == len(row):
            valid = False
            # REPORT

        else:
            obj = {k: v for k, v in zip(headers, row)}

            for k, v in zip(headers, row):
                # check type and format
                if not isinstance(v, self.schema.type(k)):
                    valid = False
                    # REPORT
                    # DO FORMAT

                # CONSTRAINTS
                constraints = self.schema.constraints('k')
                if constraints:
                    # check constraints.required
                    if constraints.get('required') and not v:
                        valid = False
                        # REPORT

                    # TODO: check constraints.unique

                # TODO: check constraints.min* and constraints.max*

                # PRIMARY KEY
                primaryKey = self.schema.primaryKey()
                if primaryKey:
                    if isinstance(primaryKey, str):
                        pass
                # IF PK in spec, check if fields are valid

                # FOREIGN KEYS

        if self.transform:
            pass

        return valid, index, row


class InvalidJSONTableSchemaError(Exception):
    pass


class JSONTableSchema(object):

    def __init__(self, schema_source, *args, **kwargs):

        self.schema_source = schema_source
        self.as_python = self.to_python()

        if not cls.validateschema(self.as_python):
            raise InvalidJSONTableSchemaError

        self.as_json = json.dumps(self.as_python)

    @classmethod
    def validateschema(cls, schema):
        return True

    def to_python(self):

        init = utilities.load_json_source(self.schema_source)

        # turn to python types, etc. lots to do there.
        as_python = init

        return as_python

    def headers(self):
        return [f['name'] for f in self.as_python.get('fields')]

    def primaryKey(self):
        return self.as_python.get('primaryKey')

    def foreignKeys(self):
        return self.as_python.get('foreignKeys')

    def fields(self):
        return [f for f in self.as_python.get('fields')]

    def field(self, field_name):
        return [f for f in self.fields if f['name'] == field_name][0]

    def type(self, field_name):
        return self.field(field_name).get('type') or str

    def constraints(self, field_name):
        return self.field(field_name).get('constraints')
    
