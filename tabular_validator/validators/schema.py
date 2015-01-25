# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base
from .. import utilities
from .. import compat


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
                if not isinstance(v, self.schema.type(k)):
                    valid = False
                    self.report.write({
                        'name': 'Incorrect type',
                        'category': 'row',
                        'level': 'error',
                        'position': index,
                        'message': ('The cell {0} is of the wrong '
                                    'type'.format(k))
                    })

                #TODO: Check format

                # CONSTRAINTS
                constraints = self.schema.constraints('k')
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

    @classmethod
    def validateschema(cls, schema):
        """Validate as JSON Table Schema based on RFC 1.0.pre-4.

        This is a bit ugly. Aims to provide complete spec coverage.
        Plan to clean up and pull put into own module.

        """

        _validation_errors = []

        # a schema is a hash
        if not isinstance(schema, dict):
            _validation_errors.append('The schema is not a hash')

        # which MUST contain a key `fields`
        if not schema.get('fields'):
            _validation_errors.append('does not contain a `fields` key')

        # `fields` MUST be an array
        if not isinstance(schema.get('fields'), list):
            _validation_errors.append('The `fields` key is present but is not an array')

        # each entry in the `fields` array MUST be a hash
        if not all([isinstance(o, dict) for o in schema['fields']]):
            _validation_errors.append('One or more of the descriptors in `fields` is not a hash')

        # each entry in the `fields` array MUST have a `name` key
        if not all([o.get('name') for o in schema['fields']]):
            _validation_errors.append('One or more of the descriptors in `fields` does not have a `name` key')

        # each entry in the `fields` array MAY have a `constraints` key
        # if `constraints` is present, then `constraints` MUST be a hash
        if not all([isinstance(o['constraints'], dict) for o in
                   schema['fields'] if o.get('constraints')]):
            _validation_errors.append('One or more of the descriptors in `fields` has a `constraints` key which is not a hash')

        # constraints may contain certain keys (each has a specific meaning)
        for constraints, _type in [(o['constraints'], o.get('type')) for o in
                                   schema['fields'] if
                                   o.get('constraints')]:

            # IF `required` key, then it is a boolean
            if constraints.get('required') and not \
                    isinstance(constraints['required'], bool):
                _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `required` key which is not boolean')

            # IF `minLength` key, then it is an integer
            if constraints.get('minLength') and not \
                    isinstance(constraints['minLength'], int):
                _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minLength` key which is not an integer')

            # IF `maxLength` key, then it is an integer
            if constraints.get('maxLength') and not \
                    isinstance(constraints['maxLength'], int):
                _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maxLength` key which is not an integer')

            # IF `unique` key, then it is a boolean
            if constraints.get('unique') and not \
                    isinstance(constraints['unique'], bool):
                _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `unique` key which is not boolean')

            # IF `pattern` key, then it is a regex
            if constraints.get('pattern') and not \
                    isinstance(constraints['pattern'], compat.str):
                _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `pattern` key which is not a string')

            # IF `minimum` key, then it DEPENDS on `field` TYPE
            if constraints.get('minimum'):

                # IF `type` is integer
                if isinstance(_type, int) and not \
                        isinstance(constraints['minimum'], int):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minimum` key with a mismatched type to its associated field')

                # IF `type` is date
                elif isinstance(_type, datetime.date) and not \
                        isinstance(constraints['minimum'], datetime.date):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minimum` key with a mismatched type to its associated field')

                # IF `type` is time
                elif isinstance(_type, datetime.time) and not \
                        isinstance(constraints['minimum'], datetime.time):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minimum` key with a mismatched type to its associated field')

                # IF `type` is datetime
                elif isinstance(_type, datetime.datetime) and not \
                        isinstance(constraints['minimum'], datetime.datetime):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minimum` key with a mismatched type to its associated field')

                else:
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `minimum` key with unclear application to its field')

            # IF `maximum` key, then it DEPENDS on `field` TYPE
            if constraints.get('maximum'):

                # IF `type` is integer
                if isinstance(_type, int) and not \
                        isinstance(constraints['maximum'], int):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maximum` key with a mismatched type to its associated field')

                # IF `type` is date
                elif isinstance(_type, datetime.date) and not \
                        isinstance(constraints['maximum'], datetime.date):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maximum` key with a mismatched type to its associated field')

                # IF `type` is time
                elif isinstance(_type, datetime.time) and not \
                        isinstance(constraints['maximum'], datetime.time):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maximum` key with a mismatched type to its associated field')

                # IF `type` is datetime
                elif isinstance(_type, datetime.datetime) and not \
                        isinstance(constraints['maximum'], datetime.datetime):
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maximum` key with a mismatched type to its associated field')

                else:
                    _validation_errors.append('A `constraints` descriptor in one or more field descriptors has a `maximum` key with unclear application to its field')

        # the hash MAY contain a key `primaryKey`
        if schema.get('primaryKey'):

            # `primaryKey` MUST be a string or an array
            if not isinstance(schema['primaryKey'], (compat.str, list)):
                _validation_errors.append('A `primaryKey` key is present but it is not an array or string')

            # ensure that the primary key matches field names
            if isinstance(schema['primaryKey'], compat.str) and \
                    not schema['primaryKey'] in \
                        [f['name'] for f in schema['fields']]:
                _validation_errors.append('The `primaryKey` does not match a name in any field descriptor')

            else:
                for k in schema['primaryKey']:
                    if not k in [f['name'] for f in schema['fields']]:
                        _validation_errors.append('A key in `primaryKey` does not match a name in any field descriptor')

        # the hash may contain a key `foreignKeys`
        if schema.get('foreignKeys'):

            # `foreignKeys` MUST be an array
            if not isinstance(schema['foreignKeys'], list):
                _validation_errors.append('A `foreignKeys` key is present but it is not an array')

            # each `foreignKey` in `foreignKeys` MUST be a hash
            if not all([isinstance(o, dict) for o in
                       schema['foreignKeys']]):
                _validation_errors.append('At least one `foreignKey` in `foreignKeys` key is not a hash')

            # each `foreignKey` in `foreignKeys` MUST have a `fields` key
            if not all([o.get('fields') for o in
                       schema['foreignKeys']]):
                _validation_errors.append('At least one `foreignKey` in `foreignKeys` key does not have a `fields` key')

            # each `fields` key in a `foreignKey` MUST be a string or array
            if not all([isinstance(o.get('fields'), (compat.str, list))
                       for o in schema['foreignKeys']]):
                _validation_errors.append('At least one `foreignKey` in `foreignKeys` key has a `fields` key that is not a string or array')

            for fk in schema['foreignKeys']:

                # ensure that `foreignKey.fields` match field names
                if isinstance(fk.get('fields'), compat.str):
                    if fk.get('fields') not in [f['name'] for f in
                                                schema['fields']]:
                        _validation_errors.append('A `foreignKey.fields` argument does not match a name in any field descriptor')

                else:
                    for field in fk.get('fields'):
                        if not field in [f['name'] for f in
                                         schema['fields']]:
                            _validation_errors.append('A key in a `foreignKey.fields` does not match a name in any field descriptor')

                # ensure that `foreignKey.reference` is present and is a hash
                if not isinstance(fk.get('reference'), dict):
                    _validation_errors.append('At least one `foreignKey` is missing a `reference` key, or, the `reference` key is not a hash')

                # ensure that `foreignKey.reference` has a `resource` key
                if not 'resource' in fk.get('reference', {}):
                    _validation_errors.append('At least one `foreignKey.reference` is missing a `resource` key')

                # ensure that `foreignKey.reference` has a `fields` key
                if not 'fields' in fk.get('reference', {}):
                    _validation_errors.append('At least one `foreignKey.reference` is missing a `fields` key')

                # ensure that `foreignKey.reference.fields`
                # matches outer `fields`
                if isinstance(fk.get('fields'), compat.str):
                    if not isinstance(fk['reference']['fields'], compat.str):
                        _validation_errors.append('Reference fields do match match the fields type')
                else:
                    if not len(fk.get('fields')) == len(fk['reference']['fields']):
                        _validation_errors.append('Reference fields do match match the fields array length')

        return not bool(_validation_errors)
