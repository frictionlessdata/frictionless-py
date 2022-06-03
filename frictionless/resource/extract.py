from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..interfaces import ProcessFunction
    from .resource import Resource


def extract(
    resource: "Resource",
    *,
    process: Optional[ProcessFunction] = None,
    stream: bool = False,
):
    """Extract resource rows

    Parameters:
        process? (func): a row processor function
        stream? (bool): whether to stream data

    Returns:
        Row[]: an array/stream of rows

    """
    data = read_row_stream(resource)
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
