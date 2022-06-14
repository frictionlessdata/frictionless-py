from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import builtins

if TYPE_CHECKING:
    from ..interfaces import FilterFunction, ProcessFunction
    from .resource import Resource


# TODO: accept an overriding schema (the same as checklist/pipeline)?
def extract(
    resource: "Resource",
    *,
    filter: Optional[FilterFunction] = None,
    process: Optional[ProcessFunction] = None,
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
    data = read_row_stream(resource)
    data = builtins.filter(filter, data) if filter else data
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
