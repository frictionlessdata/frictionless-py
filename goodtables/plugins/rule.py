import simpleeval
from ..check import Check
from ..plugin import Plugin
from ..errors import TaskError, BlankRowError, ConstraintError


# Plugin


class RulePlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'rule/blacklisted-value':
            return BlacklistedValueCheck(descriptor)
        if name == 'rule/sequential-value':
            return SequentialValueCheck(descriptor)
        if name == 'rule/custom-constraint':
            return CustomConstraintCheck(descriptor)


# Errors


class BlacklistedValueError(ConstraintError):
    code = 'rule/blacklisted-value'
    name = 'Blacklisted Value'
    tags = ['#body', '#rule']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value is blacklisted.'


class SequentialValueError(ConstraintError):
    code = 'rule/sequential-value'
    name = 'Sequential Value'
    tags = ['#body', '#rule']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value is not sequential.'


class CustomConstraintError(BlankRowError):
    code = 'rule/custom-constraint'
    name = 'Custom Constaint'
    tags = ['#body', '#rule']
    message = 'The row at position {rowPosition} has an error: {details}'
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
        cell = row[self['fieldName']]
        if cell in self['blacklist']:
            error = row.create_error_from_cell(
                BlacklistedValueError,
                field_name=self['fieldName'],
                details='blacklisted values are "%s"' % self['blacklist'],
            )
            return [error]
        return []


class SequentialValueCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'requred': ['fieldName'],
        'properties': {'fieldName': {'type': 'string'}},
    }
    possible_Errors = [  # type: ignore
        SequentialValueError
    ]

    def prepare(self):
        self.cursor = None
        self.exited = False

    def validate_task(self):
        if self['fieldName'] not in self.schema.field_names:
            details = 'sequential value check requires field "%s"' % self['fieldName']
            return [TaskError(details=details)]
        return []

    def validate_row(self, row):
        if not self.exited:
            cell = row[self['fieldName']]
            try:
                self.cursor = self.cursor or cell
                assert self.cursor == cell
                self.cursor += 1
            except Exception:
                self.exited = True
                error = row.create_error_from_cell(
                    SequentialValueError,
                    field_name=self['fieldName'],
                    details='the value is not sequential',
                )
                return [error]
        return []


class CustomConstraintCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'requred': ['constraint'],
        'properties': {'constraint': {'type': 'string'}},
    }
    possible_Errors = [  # type: ignore
        CustomConstraintError
    ]

    def validate_row(self, row):
        try:
            # This call should be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            assert simpleeval.simple_eval(self['constraint'], names=row)
        except Exception:
            error = row.create_error(
                CustomConstraintError,
                details='the custom constraint to conform is "%s"' % self['constraint'],
            )
            return [error]
        return []
