from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Optional, Iterable, List, Type
from .metadata import Metadata
from . import errors

if TYPE_CHECKING:
    from .row import Row
    from .error import Error
    from .resource import Resource
    from .interfaces import CheckFunction


# TODO: sync API with Step?
# TODO: add support for validate_package?
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

    code: str = "check"
    Errors: List[Type[Error]] = []  # type: ignore

    def __init__(self, descriptor=None, *, function: Optional["CheckFunction"] = None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.__function = function

    @property
    def resource(self) -> Resource:
        """
        Returns:
            Resource?: resource object available after the `check.connect` call
        """
        return self.__resource

    def connect(self, resource: Resource):
        """Connect to the given resource

        Parameters:
            resource (Resource): data resource
        """
        self.__resource = resource

    # Validate

    def validate_start(self) -> Iterable[Error]:
        """Called to validate the resource after opening

        Yields:
            Error: found errors
        """
        yield from []

    def validate_row(self, row: Row) -> Iterable[Error]:
        """Called to validate the given row (on every row)

        Parameters:
            row (Row): table row

        Yields:
            Error: found errors
        """
        yield from self.__function(row) if self.__function else []

    def validate_end(self) -> Iterable[Error]:
        """Called to validate the resource before closing

        Yields:
            Error: found errors
        """
        yield from []

    # Metadata

    metadata_Error = errors.CheckError
