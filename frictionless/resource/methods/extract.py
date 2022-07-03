from __future__ import annotations
import builtins
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...interfaces import IFilterFunction, IProcessFunction
    from ..resource import Resource


def extract(
    self: Resource,
    *,
    filter: Optional[IFilterFunction] = None,
    process: Optional[IProcessFunction] = None,
    stream: bool = False,
):
    """Extract resource rows

    Parameters:
        filter? (bool): a row filter function
        process? (func): a row processor function
        stream? (bool): whether to stream data

    Returns:
        Row[]: an array/stream of rows

    """
    data = read_row_stream(self)
    data = builtins.filter(filter, data) if filter else data
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
