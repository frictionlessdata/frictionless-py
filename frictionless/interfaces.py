from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, BinaryIO, TextIO, Iterable, List, Any, Union

if TYPE_CHECKING:
    from .row import Row
    from .error import Error
    from .package import Package
    from .resource import Resource


# General


IDescriptor = Union[str, dict]
IByteStream = BinaryIO
ITextStream = TextIO
IListStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]


# Functions


class CheckFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Error]:
        ...


class EncodingFunction(Protocol):
    def __call__(self, buffer: IBuffer) -> str:
        ...


class FilterFunction(Protocol):
    def __call__(self, row: Row) -> bool:
        ...


class ProcessFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Any]:
        ...


class StepFunction(Protocol):
    def __call__(self, source: Union[Resource, Package]) -> None:
        ...
