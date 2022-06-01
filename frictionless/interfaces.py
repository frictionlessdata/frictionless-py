from typing import NewType, BinaryIO, TextIO, Iterable, List, Any


IByteStream = BinaryIO
ITextStream = TextIO
IListStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]
