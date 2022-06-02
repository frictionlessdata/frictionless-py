from __future__ import annotations
from typing import NewType, BinaryIO, TextIO, Iterable, List, Any


# General


IByteStream = BinaryIO
ITextStream = TextIO
IListStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]
