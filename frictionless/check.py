from .metadata import Metadata
from . import errors


class Check(Metadata):
    """Check representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Checks`

    It's an interface for writing Frictionless checks.

    Parameters:
        descriptor? (str|dict): schema descriptor

    Raises:
        FrictionlessException: raise if metadata is invalid

    """

    code = "check"
    Errors = []  # type: ignore

    def __init__(self, descriptor=None, *, function=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.__function = function

    @property
    def resource(self):
        """
        Returns:
            Resource?: resource object available after the `check.connect` call
        """
        return self.__resource

    def connect(self, resource):
        """Connect to the given resource

        Parameters:
            resource (Resource): data resource
        """
        self.__resource = resource

    def prepare(self):
        """Called before validation"""
        pass

    # Validate

    def validate_check(self):
        """Called to validate the check itself

        Yields:
            Error: found errors
        """
        yield from []

    def validate_source(self):
        """Called to validate the given source

        Yields:
            Error: found errors
        """
        yield from []

    def validate_schema(self):
        """Called to validate the given schema

        Parameters:
            schema (Schema): table schema

        Yields:
            Error: found errors
        """
        yield from []

    def validate_header(self):
        """Called to validate the given header

        Parameters:
            header (Header): table header

        Yields:
            Error: found errors
        """
        yield from []

    def validate_row(self, row):
        """Called to validate the given row (on every row)

        Parameters:
            row (Row): table row

        Yields:
            Error: found errors
        """
        if self.__function:
            yield from self.__function(row)
            return
        yield from []

    def validate_table(self):
        """Called to validate the table (after no rows left)

        Yields:
            Error: found errors
        """
        yield from []

    # Metadata

    metadata_strict = True
    metadata_Error = errors.CheckError
