from __future__ import annotations
from typing import TYPE_CHECKING, Type, Union, List
from .platform import platform

if TYPE_CHECKING:
    from .error import Error


class FrictionlessException(Exception):
    """Main Frictionless exception

    Parameters:
        error (Error): an underlaying error

    """

    def __init__(self, error: Union[str, Error], *, reasons: List[Error] = []):
        ErrorClass: Type[Error] = platform.frictionless.Error
        self.__error = error if isinstance(error, ErrorClass) else ErrorClass(note=error)  # type: ignore
        self.__reasons = reasons
        message = f"[{self.error.type}] {self.error.message}"
        message += " " + " ".join(f"({reason.message})" for reason in reasons)
        super().__init__(message)

    @property
    def error(self) -> Error:
        return self.__error

    @property
    def reasons(self) -> List[Error]:
        return self.__reasons

    # Convert

    def to_errors(self) -> List[Error]:
        return self.__reasons if self.__reasons else [self.__error]
