from .. import helpers
from ..check import Check
from ..errors import SizeError, HashError


# TODO: add metadata profile to validate descriptor
class IntegrityCheck(Check):
    def validate_finish(self):
        errors = []

        # Size error
        if self['size']:
            if self['size'] != self.stream.size:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (self['size'], self.stream.size)
                errors.append(SizeError(details=details))

        # Hash error
        if self['hash']:
            hashing_digest = helpers.parse_hashing_digest(self['hash'])
            if hashing_digest != self.stream.hash:
                details = 'expected is "%s" and actual is "%s"'
                details = details % (hashing_digest, self.stream.hash)
                errors.append(HashError(details=details))

        return errors
