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
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'incorrect_headers': {
        'id': 'incorrect_headers',
        'name': 'Incorrect Headers',
        'msg': 'The headers do not match the schema.'
    },
    'invalid_foreignkey_reference_names': {
        'id': 'invalid_foreignkey_reference_names',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must match field names.'
    },
    'invalid_foreignkey_reference_value': {
        'id': 'invalid_foreignkey_reference_value',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema must have a fields key.'
    },
    'invalid_foreignkey_reference_fields': {
        'id': 'invalid_foreignkey_reference_fields',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must have a fields key.'
    },
    'invalid_foreignkey_reference_type': {
        'id': 'invalid_foreignkey_reference_type',
        'name': 'Invalid Type for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.refernce must be a hash.'
    },
    'invalid_foreignkey_reference_value': {
        'id': 'invalid_foreignkey_reference_value',
        'name': 'Invalid Value for foreignKey Reference',
        'msg': 'A JSON Table Schema foreignKey.reference must have a resource key.'
    },
    'invalid_foreignkey_field': {
        'id': 'invalid_foreignkey_field',
        'name': 'Invalid Value in foreignKey Field',
        'msg': 'A JSON Table Schema foreignKey.fields value must correspond with field names.'
    },
    'invalid_foreignkey_fields': {
        'id': 'invalid_foreignkey_fields',
        'name': 'Invalid Value in foreignKey Fields',
        'msg': 'A JSON Table Schema foreignKey.fields value must correspond with field names.'
    },
    'invalid_foreignkey_field_type': {
        'id': 'invalid_foreignkey_field_type',
        'name': 'Invalid Field Type in foreignKey',
        'msg': 'A JSON Table Schema foreignKey.fields type must be a string or an array.'
    },
    'invalid_foreignkey_value': {
        'id': 'invalid_foreignkey_value',
        'name': 'Invalid foreignKey Value',
        'msg': 'A JSON Table Schema foreignKey must have a fields key.'
    },
    'invalid_foreignkey_type': {
        'id': 'invalid_foreignkey_type',
        'name': 'Invalid foreignKey Type',
        'msg': 'A JSON Table Schema foreignKey must be a hash.'
    },
    'invalid_foreignkeys_type': {
        'id': 'invalid_foreignkeys_type',
        'name': 'Invalid foreignKeys Type',
        'msg': 'A JSON Table Schema foreignKeys must be an array.'
    },
    'invalid_primarykey_value': {
        'id': 'invalid_primarykey_value',
        'name': 'Invalid primaryKey Value',
        'msg': 'A JSON Table Schema primaryKey value must be present in the schema field names.'
    },
    'invalid_primarykey_type': {
        'id': 'invalid_primarykey_type',
        'name': 'Invalid primaryKey Type',
        'msg': 'A JSON Table Schema primaryKey must be either a string or an array.'
    },
    'invalid_maximum_constraint_not_supported': {
        'id': 'invalid_maximum_constraint_not_supported',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint is present with unclear application (field is not an integer or a date).'
    },
    'invalid_maximum_constraint_datetime': {
        'id': 'invalid_maximum_constraint_datetime',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a datetime is only valid if the encompassing field is also a datetime.'
    },
    'invalid_maximum_constraint_time': {
        'id': 'invalid_maximum_constraint_time',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a time is only valid if the encompassing field is also a time.'
    },
    'invalid_maximum_constraint_date': {
        'id': 'invalid_maximum_constraint_date',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a date is only valid if the encompassing field is also a date.'
    },
    'invalid_maximum_constraint_integer': {
        'id': 'invalid_maximum_constraint_integer',
        'name': 'Invalid Maximum Constraint',
        'msg': 'A JSON Table Schema maximum constraint which is a integer is only valid if the encompassing field is also a integer.'
    },
    'invalid_minimum_constraint_not_supported': {
        'id': 'invalid_minimum_constraint_not_supported',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint is present with unclear application (field is not an integer or a date).'
    },
    'invalid_minimum_constraint_datetime': {
        'id': 'invalid_minimum_constraint_datetime',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a datetime is only valid if the encompassing field is also a datetime.'
    },
    'invalid_minimum_constraint_time': {
        'id': 'invalid_minimum_constraint_time',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a time is only valid if the encompassing field is also a time.'
    },
    'invalid_minimum_constraint_date': {
        'id': 'invalid_minimum_constraint_date',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a date is only valid if the encompassing field is also a date.'
    },
    'invalid_minimum_constraint_integer': {
        'id': 'invalid_minimum_constraint_integer',
        'name': 'Invalid Minimum Constraint',
        'msg': 'A JSON Table Schema minimum constraint which is a integer is only valid if the encompassing field is also a integer.'
    },
    'invalid_pattern_constraint': {
        'id': 'invalid_pattern_constraint',
        'name': 'Invalid Pattern Constraint',
        'msg': 'A JSON Table Schema pattern constraint must be a string.'
    },
    'invalid_unique_constraint': {
        'id': 'invalid_unique_constraint',
        'name': 'Invalid Unique Constraint',
        'msg': 'A JSON Table Schema unique constraint must be a boolean.'
    },
    'invalid_maxlength_integer': {
        'id': 'invalid_maxlength_integer',
        'name': 'Invalid maxLength Value',
        'msg': 'A JSON Table Schema maxLength constraint must be an integer.'
    },
    'invalid_minlength_integer': {
        'id': 'invalid_minlength_integer',
        'name': 'Invalid minLength Value',
        'msg': 'A JSON Table Schema minLength constraint must be an integer.'
    },
    'invalid_required_constraint': {
        'id': 'invalid_required_constraint',
        'name': 'Invalid Required Constraint',
        'msg': 'A JSON Table Schema required constraint must be a boolean.'
    },
    'incomplete_field': {
        'id': 'incomplete_field',
        'name': 'Incomplete Field',
        'msg': 'A JSON Table Schema field must have a name key.'
    },
    'invalid_field': {
        'id': 'invalid_field',
        'name': 'Invalid Field',
        'msg': 'Each field in a JSON Table Schema must be a hash.'
    },
    'invalid_field_constraints': {
        'id': 'invalid_field_constraints',
        'name': 'Invalid Field Constraints',
        'msg': 'A JSON Table Schema field constraint must be a hash.'
    },
    'invalid_fields': {
        'id': 'invalid_fields',
        'name': 'Invalid Fields',
        'msg': 'A JSON Table Schema must have an array of fields.'
    },
    'invalid_schema': {
        'id': 'invalid_schema',
        'name': 'Invalid Schema',
        'msg': 'A JSON Table Schema must be a hash.'
    },
    'missing_fields': {
        'id': 'missing_fields',
        'name': 'Missing Fields',
        'msg': 'A JSON Table Schema must have a fields key.'
    },
    'invalid_foreignkey_reference_value': {
        'id': 'invalid_foreignkey_reference_value',
        'name': 'Invalid Value for foreignKey Reference',
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
        _type = RESULTS['invalid_schema']
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
        _type = RESULTS['missing_fields']
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
        _type = RESULTS['invalid_fields']
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
        _type = RESULTS['invalid_field']
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
        _type = RESULTS['incomplete_field']
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
        _type = RESULTS['invalid_field_constraints']
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
            _type = RESULTS['invalid_required_constraint']
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
            _type = RESULTS['invalid_minlength_integer']
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
            _type = RESULTS['invalid_maxlength_integer']
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
            _type = RESULTS['invalid_unique_constraint']
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
            _type = RESULTS['invalid_pattern_constraint']
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
                _type = RESULTS['invalid_minimum_constraint_integer']
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
                _type = RESULTS['invalid_minimum_constraint_date']
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
                _type = RESULTS['invalid_minimum_constraint_time']
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
                _type = RESULTS['invalid_minimum_constraint_datetime']
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
                _type = RESULTS['invalid_minimum_constraint_not_supported']
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
                _type = RESULTS['invalid_maximum_constraint_integer']
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
                _type = RESULTS['invalid_maximum_constraint_date']
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
                _type = RESULTS['invalid_maximum_constraint_time']
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
                _type = RESULTS['invalid_maximum_constraint_datetime']
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
                _type = RESULTS['invalid_maximum_constraint_not_supported']
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
            _type = RESULTS['invalid_primarykey_type']
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
                _type = RESULTS['invalid_primarykey_value']
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
                    _type = RESULTS['invalid_primarykey_value']
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
            _type = RESULTS['invalid_foreignkeys_type']
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
            _type = RESULTS['invalid_foreignkey_type']
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
            _type = RESULTS['invalid_foreignkey_value']
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
            _type = RESULTS['invalid_foreignkey_field_type']
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
                    _type = RESULTS['invalid_foreignkey_fields']
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
                        _type = RESULTS['invalid_foreignkey_field']
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
                _type = RESULTS['invalid_foreignkey_reference_type']
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
                _type = RESULTS['invalid_foreignkey_reference_value']
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
                _type = RESULTS['invalid_foreignkey_reference_fields']
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
                    _type = RESULTS['invalid_foreignkey_reference_names']
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
                    _type = RESULTS['invalid_foreignkey_reference_value']
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
