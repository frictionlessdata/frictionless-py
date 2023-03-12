from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from ..exception import FrictionlessException
from ..platform import platform
from ..resource import Resource

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction


def extract(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    # Extract
    filter: Optional[IFilterFunction] = None,
    process: Optional[IProcessFunction] = None,
    limit_rows: Optional[int] = None,
    # Deprecated
    resource_name: Optional[str] = None,
    **options,
):
    """Extract rows

    Parameters:
        name: extract only resource having this name
        filter: row filter function
        process: row processor function
        limit_rows: limit amount of rows to this number

    Returns:
        extracted rows indexed by resource name
    """
    name = name or resource_name
    resource = Resource(source, datatype=type or "", **options)
    if not isinstance(resource, platform.frictionless_resources.Extractable):
        note = f'Resource with data type "{resource.datatype}" is not convertible'
        raise FrictionlessException(note)
    return resource.extract(
        name=name, filter=filter, process=process, limit_rows=limit_rows
    )
