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

    # Validate

    def validate_row(self, row):
        yield from []

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
