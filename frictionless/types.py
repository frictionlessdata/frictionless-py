from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO, Dict, Iterable, List, Literal
from typing import Protocol, TextIO, Union

if TYPE_CHECKING:
    from .error import Error
    from .package import Package
    from .resource import Resource
    from .table import Row


# General


IStandards = Literal["v1", "v2"]
IDescriptor = Dict[str, Any]
IByteStream = BinaryIO
ITextStream = TextIO
# TODO: fix streaming types (support next)
ICellStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]
IFragment = List[List[Any]]
ILabels = List[str]
IOnerror = Literal["ignore", "warn", "raise"]
ITabularData = Dict[str, List[Dict[str, Any]]]


# Functions


class ICheckFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Error]:
        ...


class IEncodingFunction(Protocol):
    def __call__(self, buffer: IBuffer) -> str:
        ...


class IFilterFunction(Protocol):
    def __call__(self, row: Row) -> bool:
        ...


class IProcessFunction(Protocol):
    def __call__(self, row: Row) -> Dict[str, Any]:
        ...


class ICallbackFunction(Protocol):
    def __call__(self, row: Row) -> None:
        ...


class IStepFunction(Protocol):
    def __call__(self, source: Union[Resource, Package]) -> None:
        ...
