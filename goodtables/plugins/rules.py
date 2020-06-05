#  import simpleeval
from ..check import Check
from ..plugin import Plugin
from ..errors import TaskError, ConstraintError


# Plugin


class RulesPlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'rules/blacklisted-value':
            return BlacklistedValueCheck(descriptor)
        if name == 'rules/sequential-value':
            return SequentialValueCheck(descriptor)
        if name == 'rules/custom-constraint':
            return CustomConstraintCheck(descriptor)


# Errors


class BlacklistedValueError(ConstraintError):
    code = 'rules/blacklisted-value'
    name = 'Blacklisted Value'
    tags = ['#body', '#rules']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value is blacklisted.'


class SequentialValueError(ConstraintError):
    code = 'rules/sequential-value'
    name = 'Sequential Value'
    tags = ['#body', '#rules']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value is not sequential.'


class CustomConstraintError(ConstraintError):
    code = 'rules/custom-constraint'
    name = 'Custom Constaint'
    tags = ['#body', '#rules']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value does not conform to the custom constaint.'


# Checks


class BlacklistedValueCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'requred': ['fieldName', 'blacklist'],
        'properties': {'fieldName': {'type': 'string'}, 'blacklist': {'type': 'array'}},
    }
    possible_Errors = [  # type: ignore
        BlacklistedValueError
    ]

    def validate_task(self):
        if self['fieldName'] not in self.schema.field_names:
            details = 'blacklisted value check requires field "%s"' % self['fieldName']
            return [TaskError(details=details)]
        return []

    def validate_row(self, row):
        if row[self['fieldName']] in self['blacklist']:
            Error = BlacklistedValueError
            details = 'blacklisted values are "%s"' % self['blacklist']
            error = row.create_error(Error, field_name=self['fieldName'], details=details)
            return [error]
        return []


class SequentialValueCheck(Check):
    pass


class CustomConstraintCheck(Check):
    pass
