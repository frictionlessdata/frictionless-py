#  import statistics
from ..check import Check
from ..plugin import Plugin
from ..errors import Error


# Plugin


class StatsPlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'stats/duplicate-row':
            return DuplicateRowCheck(descriptor)
        if name == 'stats/deviated-value':
            return DeviatedValueCheck(descriptor)
        if name == 'stats/truncated-value':
            return TruncatedValueCheck(descriptor)


# Checks


class DuplicateRowCheck(Check):
    pass


class DeviatedValueCheck(Check):
    pass


class TruncatedValueCheck(Check):
    pass


# Errors


class DuplicateRowError(Error):
    pass


class DeviatedValueError(Error):
    pass


class TruncatedValueError(Error):
    pass
