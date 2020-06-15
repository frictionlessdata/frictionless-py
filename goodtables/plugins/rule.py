import simpleeval
from .. import errors
from ..check import Check
from ..plugin import Plugin


# Plugin


class RulePlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'rule/blacklisted-value':
            return BlacklistedValueCheck(descriptor)
        if name == 'rule/sequential-value':
            return SequentialValueCheck(descriptor)
        if name == 'rule/row-constraint':
            return RowConstraintCheck(descriptor)


# Errors


class BlacklistedValueError(errors.CellError):
    code = 'rule/blacklisted-value'
    name = 'Blacklisted Value'
    tags = ['#body', '#rule']
    template = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}'
    description = 'The value is blacklisted.'


class SequentialValueError(errors.CellError):
    code = 'rule/sequential-value'
    name = 'Sequential Value'
    tags = ['#body', '#rule']
    template = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}'
    description = 'The value is not sequential.'


class RowConstraintError(errors.RowError):
    code = 'rule/row-constraint'
    name = 'Row Constraint'
    tags = ['#body', '#rule']
    template = 'The row at position {rowPosition} has an error: {note}'
    description = 'The value does not conform to the row constraint.'


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

    def prepare(self):
        self.field_name = self['fieldName']
        self.blacklist = self['blacklist']

    # Validate

    def validate_task(self):
        if self.field_name not in self.schema.field_names:
            note = 'blacklisted value check requires field "%s"' % self.field_name
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell = row[self.field_name]
        if cell in self.blacklist:
            yield BlacklistedValueError.from_row(
                row,
                note='blacklisted values are "%s"' % self.blacklist,
                field_name=self.field_name,
            )


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
        self.field_name = self.get('fieldName')

    # Validate

    def validate_task(self):
        if self.field_name not in self.schema.field_names:
            note = 'sequential value check requires field "%s"' % self.field_name
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        if not self.exited:
            cell = row[self.field_name]
            try:
                self.cursor = self.cursor or cell
                assert self.cursor == cell
                self.cursor += 1
            except Exception:
                self.exited = True
                yield SequentialValueError.from_row(
                    row, note='the value is not sequential', field_name=self.field_name,
                )


class RowConstraintCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'requred': ['constraint'],
        'properties': {'constraint': {'type': 'string'}},
    }
    possible_Errors = [  # type: ignore
        RowConstraintError
    ]

    def prepare(self):
        self.constraint = self['constraint']

    # Validate

    def validate_row(self, row):
        try:
            # This call should be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            assert simpleeval.simple_eval(self.constraint, names=row)
        except Exception:
            yield RowConstraintError.from_row(
                row, note='the row constraint to conform is "%s"' % self.constraint,
            )
