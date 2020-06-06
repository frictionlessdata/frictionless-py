import statistics
from ..check import Check
from ..plugin import Plugin
from ..errors import Error, TaskError, RowError, CellError


# Plugin


class ProbPlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'prob/duplicate-row':
            return DuplicateRowCheck(descriptor)
        if name == 'prob/deviated-value':
            return DeviatedValueCheck(descriptor)
        if name == 'prob/truncated-value':
            return TruncatedValueCheck(descriptor)


# Errors


class DuplicateRowError(RowError):
    pass


class DeviatedValueError(Error):
    code = 'prob/deviated-value'
    name = 'Deviated Value'
    tags = ['#body', '#prob']
    message = 'There is a possible error because the value is deviated: {details}'
    description = 'The value is deviated.'


class TruncatedValueError(CellError):
    code = 'prob/truncated-value'
    name = 'Truncated Value'
    tags = ['#body', '#prob']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {details}'
    description = 'The value is possible truncated.'


# Checks


class DuplicateRowCheck(Check):
    pass


class DeviatedValueCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'requred': ['fieldName'],
        'properties': {
            'fieldName': {'type': 'string'},
            'average': {'type': ['string', 'null']},
            'interval': {'type': ['number', 'null']},
        },
    }
    possible_Errors = [  # type: ignore
        DeviatedValueError
    ]

    def prepare(self):
        self.exited = False
        self.cells = []
        self.row_positions = []
        self.field_name = self['fieldName']
        self.interval = self.get('interval', 3)
        self.average = self.get('average', 'mean')
        self.average_function = AVERAGE_FUNCTIONS.get(self.average)

    # Validate

    def validate_task(self):
        if self.field_name not in self.schema.field_names:
            details = 'deviated value check requires field "%s"' % self.field_name
            return [TaskError(details=details)]
        if not self.average_function:
            details = 'deviated value check supports only average functions "%s"'
            details = details % ', '.join(AVERAGE_FUNCTIONS.keys())
            return [TaskError(details=details)]
        return []

    def validate_row(self, row):
        try:
            cell = float(row[self.field_name])
        except ValueError:
            details = 'cell in row at position "%s" and in field "%s" must be a number'
            details = details % (row.row_position, self.field_name)
            return [DeviatedValueError(details=details)]
        self.cells.append(cell)
        self.row_positions.append(row.row_position)
        return []

    def validate_table(self):
        if len(self.cells) < 2:
            return []

        # Prepare interval
        try:
            stdev = statistics.stdev(self.cells)
            average = self.average_function(self.cells)
            minimum = average - stdev * self.interval
            maximum = average + stdev * self.interval
        except Exception as exception:
            details = 'calculation issue "%s"' % exception
            return [DeviatedValueError(details=details)]

        # Check values
        errors = []
        for row_position, cell in zip(self.row_positions, self.cells):
            if not (minimum <= cell <= maximum):
                dtl = 'value "%s" in row at position "%s" and field "%s" is deviated "[%.2f, %.2f]"'
                dtl = dtl % (cell, row_position, self.field_name, minimum, maximum)
                error = DeviatedValueError(details=dtl)
                errors.append(error)
        return errors


class TruncatedValueCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {},
    }
    possible_Errors = [  # type: ignore
        TruncatedValueError
    ]

    def validate_row(self, row):
        errors = []
        for field_name, cell in row.items():
            truncated = False

            # Skip no value
            if not cell:
                continue

            # Check string cutoff
            if isinstance(cell, str):
                if len(cell) in TRUNCATED_STRING_LENGTHS:
                    truncated = True

            # Check integer cutoff
            if isinstance(cell, int):
                if cell in TRUNCATED_INTEGER_VALUES:
                    truncated = True

            # Add error
            if truncated:
                details = 'value  is probably truncated'
                errors.append(
                    TruncatedValueError.from_row(
                        row, details=details, field_name=field_name
                    )
                )

        return errors


# Internal


AVERAGE_FUNCTIONS = {
    'mean': statistics.mean,
    'median': statistics.median,
    'mode': statistics.mode,
}
TRUNCATED_STRING_LENGTHS = [
    255,
]
TRUNCATED_INTEGER_VALUES = [
    # BigInt
    18446744073709551616,
    9223372036854775807,
    # Int
    4294967295,
    2147483647,
    # SummedInt
    2097152,
    # SmallInt
    65535,
    32767,
]
