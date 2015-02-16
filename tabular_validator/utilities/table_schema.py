# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
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
