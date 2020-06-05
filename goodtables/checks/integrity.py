from .. import helpers
from ..check import Check
from ..errors import SizeError, HashError, UniqueError, PrimaryKeyError, ForeignKeyError


class IntegrityCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'size': {'type': ['number', 'null']},
            'hash': {'type': ['string', 'null']},
        },
    }
    possible_Errors = [  # type: ignore
        # table
        SizeError,
        HashError,
        # body
        UniqueError,
        PrimaryKeyError,
        ForeignKeyError,
    ]

    def validate_table(self):
        errors = []

        # Size error
        if self.get('size'):
            if self['size'] != self.stream.size:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (self['size'], self.stream.size)
                errors.append(SizeError(details=details))

        # Hash error
        if self.get('hash'):
            hashing_digest = helpers.parse_hashing_digest(self['hash'])
            if hashing_digest != self.stream.hash:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (hashing_digest, self.stream.hash)
                errors.append(HashError(details=details))

        return errors
