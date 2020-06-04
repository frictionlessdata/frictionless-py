#  import simpleeval
from ..check import Check
from ..plugin import Plugin
from ..errors import Error


# Plugin


class RulesPlugin(Plugin):
    def create_check(self, name, *, descriptor=None):
        pass


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
