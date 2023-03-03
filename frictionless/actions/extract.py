from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from ..resource import Resource

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction


def extract(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    filter: Optional[IFilterFunction] = None,
    process: Optional[IProcessFunction] = None,
    limit_rows: Optional[int] = None,
    **options,
):
    """Extract rows

    Parameters:
        filter: row filter function
        process: row processor function
        limit_rows: limit amount of rows to this number

    Returns:
        extracted rows indexed by resource name
    """

    resource = Resource(source, datatype=type or "", **options)
    return resource.extract(filter=filter, process=process, limit_rows=limit_rows)
