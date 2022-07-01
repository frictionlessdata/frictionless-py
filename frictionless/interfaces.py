from __future__ import annotations
from pathlib import Path
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Protocol,
    BinaryIO,
    TextIO,
    Iterable,
    List,
    Dict,
    Any,
    Union,
)

if TYPE_CHECKING:
    from .table import Row
    from .error import Error
    from .package import Package
    from .resource import Resource


# General


IDescriptor = Dict[str, Any]
IDescriptorSource = Union[str, Path, Mapping]
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
