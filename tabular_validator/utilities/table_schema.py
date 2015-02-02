# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import json
import datetime
import time
import decimal
import tellme
from .. import compat
from . import helpers


def make(headers, values):

    """Return a schema from the passed headers and values.

    Args:
    * `headers`: a list of header names
    * `values`: an iterable of data (possible a sample of a whole dataset)

    Returns:
    * A JSON Table Schema as a Python dict.

    """

    # TODO: This is just a sketch out of the idea. Finish it.

    schema = {'fields': []}

    for header in headers:
        schema['fields'].append({'name': header})

    for row in values:
        assert len(row) == len(headers)

    # DO type guessing etc. See messy tables (or drop it straight in here).

    return schema


def validate(schema, report=None):

    """Validate that `schema` is a valid JSON Table Schema.

    Args:
    * `schema`: a dict to check if it is valid JSON Table Schema
    * `report`: a reporter.Report instance, otherwise a new one is created.

    Returns:
    * A tuple of `valid`, `report`

    TODO: Tidy it all up. test each condition.

    """

    valid = True

    if report is None:
        report = tellme.Report(schema=helpers.report_schema)

    # a schema is a hash
    if not isinstance(schema, dict):
        valid = False
        report.write({
            'name': 'Invalid schema',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'A JSON Table Schema should be a hash.'
        })

        # return early in this case.
        return valid, report

    # which MUST contain a key `fields`
    if not schema.get('fields'):
        valid = False
        report.write({
            'name': 'Missing `fields`',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'A JSON Table Schema must have a fields key.'
        })

        # return early in this case.
        return valid, report

    # `fields` MUST be an array
    if not isinstance(schema.get('fields'), list):
        valid = False
        report.write({
            'name': 'Invalid `fields`',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'A JSON Table Schema must have an array of fields.'
        })

        # return early in this case
        return valid, report

    # each entry in the `fields` array MUST be a hash
    if not all([isinstance(o, dict) for o in schema['fields']]):
        valid = False
        report.write({
            'name': 'Invalid `field`',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'Each field in JSON Table Schema must be a hash.'
        })

    # each entry in the `fields` array MUST have a `name` key
    if not all([o.get('name') for o in schema['fields']]):
        valid = False
        report.write({
            'name': 'Incomplete `field`',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'A JSON Table Schema field must have a name key.'
        })

    # each entry in the `fields` array MAY have a `constraints` key
    # if `constraints` is present, then `constraints` MUST be a hash
    if not all([isinstance(o['constraints'], dict) for o in
               schema['fields'] if o.get('constraints')]):
        valid = False
        report.write({
            'name': 'Invalid `contraints`',
            'category': 'schema',
            'level': 'error',
            'position': None,
            'message': 'A JSON Table Schema field contraint must be a hash.'
        })

    # constraints may contain certain keys (each has a specific meaning)
    for constraints, _type in [(o['constraints'], o.get('type'))
                               for o in schema['fields'] if
                               o.get('constraints')]:

        # IF `required` key, then it is a boolean
        if constraints.get('required') and not \
                isinstance(constraints['required'], bool):
            valid = False
            report.write({
                'name': 'Invalid `required` value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema required constraint '
                            'must be a boolean.')
            })

        # IF `minLength` key, then it is an integer
        if constraints.get('minLength') and not \
                isinstance(constraints['minLength'], int):
            valid = False
            report.write({
                'name': 'Invalid minLength value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema minLength constraint '
                            'must be an integer.')
            })

        # IF `maxLength` key, then it is an integer
        if constraints.get('maxLength') and not \
                isinstance(constraints['maxLength'], int):
            valid = False
            report.write({
                'name': 'Invalid maxLength value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema maxLength constraint '
                            'must be an integer')
            })

        # IF `unique` key, then it is a boolean
        if constraints.get('unique') and not \
                isinstance(constraints['unique'], bool):
            valid = False
            report.write({
                'name': 'Invalid unique value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema unique constraint '
                            'must be a boolean.')
            })

        # IF `pattern` key, then it is a regex
        if constraints.get('pattern') and not \
                isinstance(constraints['pattern'], compat.str):
            valid = False
            report.write({
                'name': 'Invalid pattern value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema pattern constraint '
                            'must be a string.')
            })

        # IF `minimum` key, then it DEPENDS on `field` TYPE
        if constraints.get('minimum'):

            # IF `type` is integer
            if isinstance(_type, int) and not \
                    isinstance(constraints['minimum'], int):
                valid = False
                report.write({
                    'name': 'Invalid minimum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema minimum constraint '
                                'which is an integer is only valid if the '
                                'encompassing field is also of type integer')
                })

            # IF `type` is date
            elif isinstance(_type, datetime.date) and not \
                    isinstance(constraints['minimum'], datetime.date):
                valid = False
                report.write({
                    'name': 'Invalid minimum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema minimum constraint '
                                'which is a date is only valid if the '
                                'encompassing field is also of type date')
                })

            # IF `type` is time
            elif isinstance(_type, datetime.time) and not \
                    isinstance(constraints['minimum'], datetime.time):
                valid = False
                report.write({
                    'name': 'Invalid minimum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema minimum constraint '
                                'which is a time is only valid if the '
                                'encompassing field is also of type time')
                })

            # IF `type` is datetime
            elif isinstance(_type, datetime.datetime) and not \
                    isinstance(constraints['minimum'], datetime.datetime):
                valid = False
                report.write({
                    'name': 'Invalid minimum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema minimum constraint '
                                'which is a datetime is only valid if the '
                                'encompassing field is also of type datetime')
                })

            else:
                valid = False
                report.write({
                    'name': 'Invalid minimum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema minimum constraint '
                                'is present with unclear application (field '
                                'is not an integer or a date)')
                })

        # IF `maximum` key, then it DEPENDS on `field` TYPE
        if constraints.get('maximum'):

            # IF `type` is integer
            if isinstance(_type, int) and not \
                    isinstance(constraints['maximum'], int):
                valid = False
                report.write({
                    'name': 'Invalid maximum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema maximum constraint '
                                'which is an integer is only valid if the '
                                'encompassing field is also of type integer')
                })

            # IF `type` is date
            elif isinstance(_type, datetime.date) and not \
                    isinstance(constraints['maximum'], datetime.date):
                valid = False
                report.write({
                    'name': 'Invalid maximum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema maximum constraint '
                                'which is a date is only valid if the '
                                'encompassing field is also of type date')
                })

            # IF `type` is time
            elif isinstance(_type, datetime.time) and not \
                    isinstance(constraints['maximum'], datetime.time):
                valid = False
                report.write({
                    'name': 'Invalid maximum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema maximum constraint '
                                'which is a time is only valid if the '
                                'encompassing field is also of type time')
                })

            # IF `type` is datetime
            elif isinstance(_type, datetime.datetime) and not \
                    isinstance(constraints['maximum'], datetime.datetime):
                valid = False
                report.write({
                    'name': 'Invalid maximum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema maximum constraint '
                                'which is a datetime is only valid if the '
                                'encompassing field is also of type datetime')
                })

            else:
                valid = False
                report.write({
                    'name': 'Invalid maximum value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema maximum constraint '
                                'is present with unclear application (field '
                                'is not an integer or a date)')
                })

    # the hash MAY contain a key `primaryKey`
    if schema.get('primaryKey'):

        # `primaryKey` MUST be a string or an array
        if not isinstance(schema['primaryKey'], (compat.str, list)):
            valid = False
            report.write({
                'name': 'Invalid `primaryKey` type',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': 'A JSON Table Schema primaryKey must be either '
                'a string or an array.'
            })

        # ensure that the primary key matches field names
        if isinstance(schema['primaryKey'], compat.str):
            if not schema['primaryKey'] in [f['name'] for f in schema['fields']]:
                valid = False
                report.write({
                    'name': 'Invalid `primaryKey` value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema primaryKey value must be '
                                'found in the schema field names')
                })

        else:
            for k in schema['primaryKey']:
                if not k in [f['name'] for f in schema['fields']]:
                    valid = False
                    report.write({
                        'name': 'Invalid `primaryKey` value',
                        'category': 'schema',
                        'level': 'error',
                        'position': None,
                        'message': ('A JSON Table Schema primaryKey value '
                                    'must be found in the schema field names')
                    })

    # the hash may contain a key `foreignKeys`
    if schema.get('foreignKeys'):

        # `foreignKeys` MUST be an array
        if not isinstance(schema['foreignKeys'], list):
            valid = False
            report.write({
                'name': 'Invalid `foreignKeys` type',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': 'A JSON Table Schema foreignKeys must be an array.'
            })

        # each `foreignKey` in `foreignKeys` MUST be a hash
        if not all([isinstance(o, dict) for o in
                   schema['foreignKeys']]):
            valid = False
            report.write({
                'name': 'Invalid `foreignKey` type',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': 'A JSON Table Schema `foreignKey` must be a hash.'
            })

        # each `foreignKey` in `foreignKeys` MUST have a `fields` key
        if not all([o.get('fields') for o in
                   schema['foreignKeys']]):
            valid = False
            report.write({
                'name': 'Invalid `foreignKey` value',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema foreignKey must have a '
                            'fields key.')
            })

        # each `fields` key in a `foreignKey` MUST be a string or array
        if not all([isinstance(o.get('fields'), (compat.str, list))
                   for o in schema['foreignKeys']]):
            valid = False
            report.write({
                'name': 'Invalid `foreignKey.fields` type',
                'category': 'schema',
                'level': 'error',
                'position': None,
                'message': ('A JSON Table Schema foreignKey.fields type must '
                            'be a string or an array.')
            })

        for fk in schema['foreignKeys']:

            # ensure that `foreignKey.fields` match field names
            if isinstance(fk.get('fields'), compat.str):
                if fk.get('fields') not in [f['name'] for f in
                                            schema['fields']]:
                    valid = False
                    report.write({
                        'name': 'Invalid `foreignKey.fields` value',
                        'category': 'schema',
                        'level': 'error',
                        'position': None,
                        'message': ('A JSON Table Schema foreignKey.fields '
                                    'value must correspond with field names.')
                    })

            else:
                for field in fk.get('fields'):
                    if not field in [f['name'] for f in
                                     schema['fields']]:
                        valid = False
                        report.write({
                            'name': 'Invalid `foreignKey.fields` value',
                            'category': 'schema',
                            'level': 'error',
                            'position': None,
                            'message': ('A JSON Table Schema '
                                        'foreignKey.fields value must '
                                        'correspond with field names.')
                        })

            # ensure that `foreignKey.reference` is present and is a hash
            if not isinstance(fk.get('reference'), dict):
                valid = False
                report.write({
                    'name': 'Invalid `foreignKey.reference` type',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema foreignKey.reference '
                                'must be a hash.')
                })

            # ensure that `foreignKey.reference` has a `resource` key
            if not 'resource' in fk.get('reference', {}):
                valid = False
                report.write({
                    'name': 'Invalid `foreignKey.reference` value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema foreignKey.reference '
                                'must have a resource key.')
                })

            # ensure that `foreignKey.reference` has a `fields` key
            if not 'fields' in fk.get('reference', {}):
                valid = False
                report.write({
                    'name': 'Invalid `foreignKey.reference` value',
                    'category': 'schema',
                    'level': 'error',
                    'position': None,
                    'message': ('A JSON Table Schema foreignKey.reference '
                                'must have a fields key.')
                })

            # ensure that `foreignKey.reference.fields`
            # matches outer `fields`
            if isinstance(fk.get('fields'), compat.str):
                if not isinstance(fk['reference']['fields'], compat.str):
                    valid = False
                    report.write({
                        'name': 'Invalid `foreignKey.reference` value',
                        'category': 'schema',
                        'level': 'error',
                        'position': None,
                        'message': ('A JSON Table Schema '
                                    'foreignKey.reference.fields must match '
                                    'field names.')
                    })
            else:
                if not len(fk.get('fields')) == len(fk['reference']['fields']):
                    valid = False
                    report.write({
                        'name': 'Schema has no `fields` key',
                        'category': 'schema',
                        'level': 'error',
                        'position': None,
                        'message': 'A JSON Table Schema must have a fields key.'
                    })

    return valid, report


class InvalidSchemaError(Exception):
    pass


class JSONTableSchema(object):

    def __init__(self, schema_source):

        self.schema_source = schema_source
        self.as_python = self._to_python()

        if not validate(self.as_python):
            raise InvalidSchemaError

        self.as_json = json.dumps(self.as_python)

    @property
    def headers(self):
        return [f['name'] for f in self.as_python.get('fields')]

    @property
    def primaryKey(self):
        return self.as_python.get('primaryKey')

    @property
    def foreignKeys(self):
        return self.as_python.get('foreignKeys')

    @property
    def fields(self):
        return [f for f in self.as_python.get('fields')]

    def _to_python(self):
        """Return schema as a Python data structure (dict)."""
        as_python = helpers.load_json_source(self.schema_source)
        return as_python

    def _type_map(self):
        return {
            'string': StringType(),
            'number': NumberType(),
            'integer': IntegerType(),
            'date': DateType(),
            'time': TimeType(),
            'datetime': DateTimeType(),
            'boolean': BooleanType(),
            'binary': StringType(),
            'array': ArrayType(),
            'object': ObjectType(),
            'geopoint': (StringType(), ArrayType(), ObjectType()),
            'geojson': ObjectType(),
            'any': AnyType()
        }

    def get_field(self, field_name):
        """Return the `field` object for `field_name`."""
        return [f for f in self.fields if f['name'] == field_name][0]

    def get_type(self, field_name):
        """Return the `type` for `field_name`."""
        return self._type_map()[self.get_field(field_name).get('type', 'string')]

    def get_constraints(self, field_name):
        """Return the `constraints` object for `field_name`."""
        return self.get_field(field_name).get('constraints')

    def cast(self, field_name, value):
        """Return boolean if value can be cast to field_name's type."""

        _type = self.get_type(field_name)

        if isinstance(_type, collections.Iterable):
            return any([t.cast(value) for t in _type])

        return _type.cast(value)


class TableSchemaType(object):

    py = None

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        if value in ('', None):
            return False


class StringType(TableSchemaType):

    py = compat.str

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        if value is None:
            return False
        if isinstance(value, self.py):
            return True
        return compat.str(value)


class IntegerType(TableSchemaType):

    py = int

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(IntegerType, self).cast(value)
        if isinstance(value, self.py):
            return True
        try:
            return self.py(value)
        except ValueError:
            return False


class NumberType(TableSchemaType):

    py = float, decimal.Decimal

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(NumberType, self).cast(value)
        if isinstance(value, self.py):
            return True
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            return False


class DateType(TableSchemaType):

    py = datetime.date
    format = '%Y-%m-%d'

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(DateType, self).cast(value)
        try:
            return datetime.datetime.strptime(value, self.format).date()
        except ValueError:
            return False


class TimeType(TableSchemaType):
    py = datetime.time
    format = '%H:%M:%S'

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(TimeType, self).cast(value)
        try:
            return time.strptime(value, self.format)
        except ValueError:
            return False


class DateTimeType(TableSchemaType):
    py = datetime.datetime
    format = '%Y-%m-%dT%H:%M:%SZ'

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(DateTimeType, self).cast(value)
        try:
            return datetime.datetime.strptime(value, self.format)
        except ValueError:
            return False


class BooleanType(TableSchemaType):

    py = bool
    true_values = ('yes', 'y', 'true', '0')
    false_values = ('no', 'n','false', '1')

    def __init__(self, true_values=None, false_values=None):
        if true_values is not None:
            self.true_values = true_values
        if false_values is not None:
            self.false_values = false_values

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(BooleanType, self).cast(value)
        value = value.strip().lower()
        if value in self.true_values:
            return True
        if value in self.false_values:
            return False
        return False


class ArrayType(TableSchemaType):

    py = list

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(ArrayType, self).cast(value)
        if isinstance(value, self.py):
            return True
        try:
            value = json.loads(value)
            if isinstance(value, self.py):
                return True
            else:
                return False
        except ValueError:
            return False


class ObjectType(TableSchemaType):

    py = dict

    def cast(self, value):
        """Return boolean if `value` can be cast as type `self.py`"""
        super(ObjectType, self).cast(value)
        if isinstance(value, self.py):
            return True
        try:
            value = json.loads(value)
            if isinstance(value, self.py):
                return True
            else:
                return False
        except ValueError:
            return False


class AnyType(TableSchemaType):

    def cast(self, value):
        return True
