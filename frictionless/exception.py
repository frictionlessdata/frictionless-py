from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Optional, Iterable, Union, List, Any

if TYPE_CHECKING:
    from .error import Error


class FrictionlessException(Exception):
    """Main Frictionless exception

    API      | Usage
    -------- | --------
    Public   | `from frictionless import FrictionlessException`

    Parameters:
        error (Error): an underlaying error

    """

    def __init__(self, error: Error):
        self.__error = error
        super().__init__(f"[{error.code}] {error.message}")

    @property
    def error(self) -> Error:
        """
        Returns:
            Error: error
        """
        return self.__error
