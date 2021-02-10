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

    # Validate

    def validate_start(self):
        """Called to validate the resource after opening

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
        yield from self.__function(row) if self.__function else []

    def validate_end(self):
        """Called to validate the resource before closing

        Yields:
            Error: found errors
        """
        yield from []

    # Metadata

    metadata_Error = errors.CheckError
