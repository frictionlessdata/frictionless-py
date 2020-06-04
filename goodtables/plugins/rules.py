#  import simpleeval
from ..check import Check
from ..plugin import Plugin
from ..errors import Error


# Plugin


class RulesPlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        if name == 'rules/blacklisted-value':
            return BlacklistedValueCheck(descriptor)
        if name == 'rules/sequential-value':
            return SequentialValueCheck(descriptor)
        if name == 'rules/custom-constraint':
            return CustomConstraintCheck(descriptor)


# Checks


class BlacklistedValueCheck(Check):
    pass


class SequentialValueCheck(Check):
    pass


class CustomConstraintCheck(Check):
    pass


# Errors


class BlacklistedValueError(Error):
    pass


class SequentialValueError(Error):
    pass


class CustomConstraintError(Error):
    pass
