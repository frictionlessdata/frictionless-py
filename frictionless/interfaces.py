from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, BinaryIO, TextIO, Iterable, List, Any

if TYPE_CHECKING:
    from .row import Row


# General


IByteStream = BinaryIO
ITextStream = TextIO
IListStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]


# Functions


class ProcessFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Any]:
        ...
