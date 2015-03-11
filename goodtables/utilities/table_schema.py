# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import tellme
from .. import compat
from . import helpers

RESULT_CATEGORY_SCHEMA = 'schema'
RESULT_LEVEL_INFO = 'info'
RESULT_LEVEL_WARNING = 'warning'
RESULT_LEVEL_ERROR = 'error'

RESULTS = {
    'schema_050': {
        'id': 'schema_050',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'schema_051': {
        'id': 'schema_051',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must match field names.'
    },
    'schema_052': {
        'id': 'schema_052',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema must have a fields key.'
    },
    'schema_053': {
        'id': 'schema_053',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must have a fields key.'
    },
    'schema_054': {
        'id': 'schema_054',
        'name': 'Invalid Type for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.refernce must be a hash.'
    },
    'schema_055': {
        'id': 'schema_055',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must have a resource key.'
    },
    'schema_056': {
        'id': 'schema_056',
        'name': 'Invalid Value in foreignKey Field',
        'msg': 'A JSON Table Schema foreignKey.fields value must correspond with field names.'
    },
    'schema_057': {
        'id': 'schema_057',
        'name': 'Invalid Value in foreignKey Fields',
        'msg': 'A JSON Table Schema foreignKey.fields value must correspond with field names.'
    },
    'schema_058': {
        'id': 'schema_058',
        'name': 'Invalid Field Type in foreignKey',
        'msg': 'A JSON Table Schema foreignKey.fields type must be a string or an array.'
    },
    'schema_059': {
        'id': 'schema_059',
        'name': 'Invalid foreignKey Value',
        'msg': 'A JSON Table Schema foreignKey must have a fields key.'
    },
    'schema_060': {
        'id': 'schema_060',
        'name': 'Invalid foreignKey Type',
        'msg': 'A JSON Table Schema foreignKey must be a hash.'
    },
    'schema_061': {
        'id': 'schema_061',
        'name': 'Invalid foreignKeys Type',
        'msg': 'A JSON Table Schema foreignKeys must be an array.'
    },
    'schema_062': {
        'id': 'schema_062',
        'name': 'Invalid primaryKey Value',
        'msg': 'A JSON Table Schema primaryKey value must be present in the schema field names.'
    },
    'schema_063': {
        'id': 'schema_063',
        'name': 'Invalid primaryKey Type',
        'msg': 'A JSON Table Schema primaryKey must be either a string or an array.'
    },
    'schema_064': {
        'id': 'schema_064',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint is present with unclear application (field is not an integer or a date).'
    },
    'schema_065': {
        'id': 'schema_065',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a datetime is only valid if the encompassing field is also a datetime.'
    },
    'schema_066': {
        'id': 'schema_066',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a time is only valid if the encompassing field is also a time.'
    },
    'schema_067': {
        'id': 'schema_067',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a date is only valid if the encompassing field is also a date.'
    },
    'schema_068': {
        'id': 'schema_068',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a integer is only valid if the encompassing field is also a integer.'
    },
    'schema_069': {
        'id': 'schema_069',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint is present with unclear application (field is not an integer or a date).'
    },
    'schema_070': {
        'id': 'schema_070',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a datetime is only valid if the encompassing field is also a datetime.'
    },
    'schema_071': {
        'id': 'schema_071',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a time is only valid if the encompassing field is also a time.'
    },
    'schema_072': {
        'id': 'schema_072',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a date is only valid if the encompassing field is also a date.'
    },
    'schema_073': {
        'id': 'schema_073',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a integer is only valid if the encompassing field is also a integer.'
    },
    'schema_074': {
        'id': 'schema_074',
        'name': 'Invalid Pattern Constraint',
        'msg': 'A JSON Table Schema pattern constraint must be a string.'
    },
    'schema_075': {
        'id': 'schema_075',
        'name': 'Invalid Unique Constraint',
        'msg': 'A JSON Table Schema unique constraint must be a boolean.'
    },
    'schema_076': {
        'id': 'schema_076',
        'name': 'Invalid maxLength Value',
        'msg': 'A JSON Table Schema maxLength constraint must be an integer.'
    },
    'schema_077': {
        'id': 'schema_077',
        'name': 'Invalid minLength Value',
        'msg': 'A JSON Table Schema minLength constraint must be an integer.'
    },
    'schema_078': {
        'id': 'schema_078',
        'name': 'Invalid Required Constraint',
        'msg': 'A JSON Table Schema required constraint must be a boolean.'
    },
    'schema_079': {
        'id': 'schema_079',
        'name': 'Incomplete Field',
        'msg': 'A JSON Table Schema field must have a name key.'
    },
    'schema_080': {
        'id': 'schema_080',
        'name': 'Invalid Field',
        'msg': 'Each field in a JSON Table Schema must be a hash.'
    },
    'schema_081': {
        'id': 'schema_081',
        'name': 'Invalid Field Constraints',
        'msg': 'A JSON Table Schema field constraint must be a hash.'
    },
    'schema_082': {
        'id': 'schema_082',
        'name': 'Invalid Fields',
        'msg': 'A JSON Table Schema must have an array of fields.'
    },
    'schema_083': {
        'id': 'schema_083',
        'name': 'Invalid Schema',
        'msg': 'A JSON Table Schema must be a hash.'
    },
    'schema_084': {
        'id': 'schema_084',
        'name': 'Missing Fields',
        'msg': 'A JSON Table Schema must have a fields key.'
    },
}


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
        _type = RESULTS['schema_083']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

        # return early in this case.
        return valid, report

    # which MUST contain a key `fields`
    if not schema.get('fields'):

        valid = False
        _type = RESULTS['schema_084']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

        # return early in this case.
        return valid, report

    # `fields` MUST be an array
    if not isinstance(schema.get('fields'), list):

        valid = False
        _type = RESULTS['schema_058']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

        # return early in this case
        return valid, report

    # each entry in the `fields` array MUST be a hash
    if not all([isinstance(o, dict) for o in schema['fields']]):

        valid = False
        _type = RESULTS['schema_080']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

    # each entry in the `fields` array MUST have a `name` key
    if not all([o.get('name') for o in schema['fields']]):

        valid = False
        _type = RESULTS['schema_079']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

    # each entry in the `fields` array MAY have a `constraints` key
    # if `constraints` is present, then `constraints` MUST be a hash
    if not all([isinstance(o['constraints'], dict) for o in
               schema['fields'] if o.get('constraints')]):

        valid = False
        _type = RESULTS['schema_081']
        entry = {
            'processor': 'schema',
            'result_category': RESULT_CATEGORY_SCHEMA,
            'result_level': RESULT_LEVEL_ERROR,
            'result_message': _type['msg'],
            'result_id': _type['id'],
            'result_name': _type['name'],
            'row_index': None,
            'row_name': '',
            'column_index': None,
            'column_name': ''
        }

        report.write(entry)

    # constraints may contain certain keys (each has a specific meaning)
    for constraints, _type in [(o['constraints'], o.get('type'))
                               for o in schema['fields'] if
                               o.get('constraints')]:

        # IF `required` key, then it is a boolean
        if constraints.get('required') and not \
                isinstance(constraints['required'], bool):

            valid = False
            _type = RESULTS['schema_078']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # IF `minLength` key, then it is an integer
        if constraints.get('minLength') and not \
                isinstance(constraints['minLength'], int):

            valid = False
            _type = RESULTS['schema_077']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # IF `maxLength` key, then it is an integer
        if constraints.get('maxLength') and not \
                isinstance(constraints['maxLength'], int):

            valid = False
            _type = RESULTS['schema_076']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # IF `unique` key, then it is a boolean
        if constraints.get('unique') and not \
                isinstance(constraints['unique'], bool):

            valid = False
            _type = RESULTS['schema_075']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # IF `pattern` key, then it is a regex
        if constraints.get('pattern') and not \
                isinstance(constraints['pattern'], compat.str):

            valid = False
            _type = RESULTS['schema_074']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # IF `minimum` key, then it DEPENDS on `field` TYPE
        if constraints.get('minimum'):

            # IF `type` is integer
            if isinstance(_type, int) and not \
                    isinstance(constraints['minimum'], int):

                valid = False
                _type = RESULTS['schema_073']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is date
            elif isinstance(_type, datetime.date) and not \
                    isinstance(constraints['minimum'], datetime.date):

                valid = False
                _type = RESULTS['schema_072']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is time
            elif isinstance(_type, datetime.time) and not \
                    isinstance(constraints['minimum'], datetime.time):

                valid = False
                _type = RESULTS['schema_071']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is datetime
            elif isinstance(_type, datetime.datetime) and not \
                    isinstance(constraints['minimum'], datetime.datetime):

                valid = False
                _type = RESULTS['schema_070']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            else:

                valid = False
                _type = RESULTS['schema_069']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

        # IF `maximum` key, then it DEPENDS on `field` TYPE
        if constraints.get('maximum'):

            # IF `type` is integer
            if isinstance(_type, int) and not \
                    isinstance(constraints['maximum'], int):

                valid = False
                _type = RESULTS['schema_068']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is date
            elif isinstance(_type, datetime.date) and not \
                    isinstance(constraints['maximum'], datetime.date):

                valid = False
                _type = RESULTS['schema_067']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is time
            elif isinstance(_type, datetime.time) and not \
                    isinstance(constraints['maximum'], datetime.time):

                valid = False
                _type = RESULTS['schema_066']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # IF `type` is datetime
            elif isinstance(_type, datetime.datetime) and not \
                    isinstance(constraints['maximum'], datetime.datetime):

                valid = False
                _type = RESULTS['schema_065']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            else:

                valid = False
                _type = RESULTS['schema_064']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

    # the hash MAY contain a key `primaryKey`
    if schema.get('primaryKey'):

        # `primaryKey` MUST be a string or an array
        if not isinstance(schema['primaryKey'], (compat.str, list)):

            valid = False
            _type = RESULTS['schema_063']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # ensure that the primary key matches field names
        if isinstance(schema['primaryKey'], compat.str):
            if not schema['primaryKey'] in [f['name'] for f in schema['fields']]:

                valid = False
                _type = RESULTS['schema_062']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

        else:
            for k in schema['primaryKey']:
                if not k in [f['name'] for f in schema['fields']]:

                    valid = False
                    _type = RESULTS['schema_062']
                    entry = {
                        'processor': 'schema',
                        'result_category': RESULT_CATEGORY_SCHEMA,
                        'result_level': RESULT_LEVEL_ERROR,
                        'result_message': _type['msg'],
                        'result_id': _type['id'],
                        'result_name': _type['name'],
                        'row_index': None,
                        'row_name': '',
                        'column_index': None,
                        'column_name': ''
                    }

                    report.write(entry)

    # the hash may contain a key `foreignKeys`
    if schema.get('foreignKeys'):

        # `foreignKeys` MUST be an array
        if not isinstance(schema['foreignKeys'], list):

            valid = False
            _type = RESULTS['schema_061']
            result = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # each `foreignKey` in `foreignKeys` MUST be a hash
        if not all([isinstance(o, dict) for o in
                   schema['foreignKeys']]):

            valid = False
            _type = RESULTS['schema_058']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # each `foreignKey` in `foreignKeys` MUST have a `fields` key
        if not all([o.get('fields') for o in
                   schema['foreignKeys']]):

            valid = False
            _type = RESULTS['schema_059']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        # each `fields` key in a `foreignKey` MUST be a string or array
        if not all([isinstance(o.get('fields'), (compat.str, list))
                   for o in schema['foreignKeys']]):

            valid = False
            _type = RESULTS['schema_060']
            entry = {
                'processor': 'schema',
                'result_category': RESULT_CATEGORY_SCHEMA,
                'result_level': RESULT_LEVEL_ERROR,
                'result_message': _type['msg'],
                'result_id': _type['id'],
                'result_name': _type['name'],
                'row_index': None,
                'row_name': '',
                'column_index': None,
                'column_name': ''
            }

            report.write(entry)

        for fk in schema['foreignKeys']:

            # ensure that `foreignKey.fields` match field names
            if isinstance(fk.get('fields'), compat.str):
                if fk.get('fields') not in [f['name'] for f in
                                            schema['fields']]:

                    valid = False
                    _type = RESULTS['schema_056']
                    entry = {
                        'processor': 'schema',
                        'result_category': RESULT_CATEGORY_SCHEMA,
                        'result_level': RESULT_LEVEL_ERROR,
                        'result_message': _type['msg'],
                        'result_id': _type['id'],
                        'result_name': _type['name'],
                        'row_index': None,
                        'row_name': '',
                        'column_index': None,
                        'column_name': ''
                    }

                    report.write(entry)

            else:
                for field in fk.get('fields'):
                    if not field in [f['name'] for f in
                                     schema['fields']]:

                        valid = False
                        _type = RESULTS['schema_056']
                        entry = {
                            'processor': 'schema',
                            'result_category': RESULT_CATEGORY_SCHEMA,
                            'result_level': RESULT_LEVEL_ERROR,
                            'result_message': _type['msg'],
                            'result_id': _type['id'],
                            'result_name': _type['name'],
                            'row_index': None,
                            'row_name': '',
                            'column_index': None,
                            'column_name': ''
                        }

                        report.write(entry)

            # ensure that `foreignKey.reference` is present and is a hash
            if not isinstance(fk.get('reference'), dict):

                valid = False
                _type = RESULTS['schema_054']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # ensure that `foreignKey.reference` has a `resource` key
            if not 'resource' in fk.get('reference', {}):

                valid = False
                _type = RESULTS['schema_052']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # ensure that `foreignKey.reference` has a `fields` key
            if not 'fields' in fk.get('reference', {}):

                valid = False
                _type = RESULTS['schema_053']
                entry = {
                    'processor': 'schema',
                    'result_category': RESULT_CATEGORY_SCHEMA,
                    'result_level': RESULT_LEVEL_ERROR,
                    'result_message': _type['msg'],
                    'result_id': _type['id'],
                    'result_name': _type['name'],
                    'row_index': None,
                    'row_name': '',
                    'column_index': None,
                    'column_name': ''
                }

                report.write(entry)

            # ensure that `foreignKey.reference.fields`
            # matches outer `fields`
            if isinstance(fk.get('fields'), compat.str):
                if not isinstance(fk['reference']['fields'], compat.str):

                    valid = False
                    _type = RESULTS['schema_051']
                    entry = {
                        'processor': 'schema',
                        'result_category': RESULT_CATEGORY_SCHEMA,
                        'result_level': RESULT_LEVEL_ERROR,
                        'result_message': _type['msg'],
                        'result_id': _type['id'],
                        'result_name': _type['name'],
                        'row_index': None,
                        'row_name': '',
                        'column_index': None,
                        'column_name': ''
                    }

                    report.write(entry)

            else:
                if not len(fk.get('fields')) == len(fk['reference']['fields']):

                    valid = False
                    _type = RESULTS['schema_052']
                    entry = {
                        'processor': 'schema',
                        'result_category': RESULT_CATEGORY_SCHEMA,
                        'result_level': RESULT_LEVEL_ERROR,
                        'result_message': _type['msg'],
                        'result_id': _type['id'],
                        'result_name': _type['name'],
                        'row_index': None,
                        'row_name': '',
                        'column_index': None,
                        'column_name': ''
                    }

                    report.write(entry)

    return valid, report
