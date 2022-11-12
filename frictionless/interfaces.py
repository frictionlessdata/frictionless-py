from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Protocol, BinaryIO, TextIO, Iterable, List, Dict, Any, Union, Literal

if TYPE_CHECKING:
    from .table import Row
    from .error import Error
    from .package import Package
    from .resource import Resource


# General


IStandards = Literal["v1", "v2", "v2-strict"]
IDescriptor = Dict[str, Any]
IProfile = Dict[str, Any]
IByteStream = BinaryIO
ITextStream = TextIO
# TODO: fix streaming types (support next)
ICellStream = Iterable[List[Any]]
IRowStream = Iterable[Row]
IBuffer = bytes
ISample = List[List[Any]]
IFragment = List[List[Any]]
ILabels = List[str]
IOnerror = Literal["ignore", "warn", "raise"]


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
    def __call__(self, row: Row) -> Iterable[Any]:
        ...


class ICallbackFunction(Protocol):
    def __call__(self, row: Row) -> None:
        ...


class IStepFunction(Protocol):
    def __call__(self, source: Union[Resource, Package]) -> None:
        ...
