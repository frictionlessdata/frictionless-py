from .. import errors
from .. import helpers
from ..check import Check


class IntegrityCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'size': {'type': ['number', 'null']},
            'hash': {'type': ['string', 'null']},
            'lookup': {'type': ['object', 'null']},
        },
    }
    possible_Errors = [  # type: ignore
        # table
        errors.SizeError,
        errors.HashError,
        # body
        errors.UniqueError,
        errors.PrimaryKeyError,
        errors.ForeignKeyError,
    ]

    def prepare(self):
        self.size = self.get('size')
        self.hash = self.get('hash')
        self.lookup = self.get('lookup')
        self.memory_primary = {}
        self.memory_unique = {}
        for field in self.schema.fields:
            if field.constraints.get('unique'):
                self.memory_unique[field.name] = {}

    # Validate

    def validate_row(self, row):

        # Unique Error
        if self.memory_unique:
            for field_name in self.memory_unique.keys():
                cell = row[field_name]
                if cell is not None:
                    match = self.memory_unique[field_name].get(cell)
                    self.memory_unique[field_name][cell] = row.row_position
                    if match:
                        details = 'the same as in the row at position %s' % match
                        yield errors.UniqueError.from_row(
                            row, details=details, field_name=field_name
                        )

        # PrimaryKey Error
        if self.schema.primary_key:
            cells = tuple(row[field_name] for field_name in self.schema.primary_key)
            if set(cells) == {None}:
                details = 'cells composing the primary keys are all "None"'
                yield errors.PrimaryKeyError.from_row(row, details=details)
            else:
                match = self.memory_primary.get(cells)
                self.memory_primary[cells] = row.row_position
                if match:
                    if match:
                        details = 'the same as in the row at position %s' % match
                        yield errors.PrimaryKeyError.from_row(row, details=details)

    def validate_table(self):

        # Size error
        if self.size:
            if self.size != self.stream.size:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (self.size, self.stream.size)
                yield errors.SizeError(details=details)

        # Hash error
        if self.hash:
            hashing_digest = helpers.parse_hashing_digest(self.hash)
            if hashing_digest != self.stream.hash:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (hashing_digest, self.stream.hash)
                yield errors.HashError(details=details)
