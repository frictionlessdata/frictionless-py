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

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)

    @property
    def table(self):
        """
        Returns:
            Table?: table object available after the `check.connect` call
        """
        return self.__table

    # Validation

    def connect(self, table):
        """Connect to the given table

        Parameters:
            table (Table): data table
        """
        self.__table = table

    def prepare(self):
        """Called before validation"""
        pass

    def validate_task(self):
        """Called to validate the check itself

        Yields:
            Error: found errors
        """
        yield from []

    # TODO: we actually don't need a schema argument here as self.table is available
    def validate_schema(self, schema):
        """Called to validate the given schema

        Parameters:
            schema (Schema): table schema

        Yields:
            Error: found errors
        """
        yield from []

    # TODO: we actually don't need a header argument here as self.table is available
    def validate_header(self, header):
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
