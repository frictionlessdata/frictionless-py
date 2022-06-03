from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..interfaces import ProcessFunction
    from .package import Package


def extract(
    package: "Package",
    *,
    process: Optional[ProcessFunction] = None,
    stream: bool = False,
):
    """Extract package rows

    Parameters:
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """
    result = {}
    for number, resource in enumerate(package.resources, start=1):  # type: ignore
        key = resource.fullpath if not resource.memory else f"memory{number}"
        data = read_row_stream(resource)
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
