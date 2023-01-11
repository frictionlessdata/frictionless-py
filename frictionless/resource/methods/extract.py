from __future__ import annotations
import builtins
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...interfaces import IFilterFunction, IProcessFunction
    from ..resource import Resource


def extract(
    self: Resource,
    *,
    limit_rows: Optional[int] = None,
    process: Optional[IProcessFunction] = None,
    filter: Optional[IFilterFunction] = None,
    stream: bool = False,
):
    """Extract resource rows

    Parameters:
        process? (func): a row processor function
        filter? (bool): a row filter function
        stream? (bool): whether to stream data

    Returns:
        Row[]: an array/stream of rows

    """

    # Stream
    def read_row_stream():
        with self:
            row_count = 0
            for row in self.row_stream:  # type: ignore
                row_count += 1
                yield row
                if limit_rows and limit_rows <= row_count:
                    break

    # Return
    data = read_row_stream()
    data = builtins.filter(filter, data) if filter else data
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)
