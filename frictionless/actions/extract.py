from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ..exception import FrictionlessException
from ..platform import platform
from ..resource import Resource

if TYPE_CHECKING:
    from .. import types


def extract(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    # Extract
    filter: Optional[types.IFilterFunction] = None,
    process: Optional[types.IProcessFunction] = None,
    limit_rows: Optional[int] = None,
    # Deprecated
    resource_name: Optional[str] = None,
    **options: Any,
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

    # Create resource
    resource = (
        source
        if isinstance(source, Resource)
        else Resource(source, datatype=type, **options)
    )

    # Extract resource
    if not isinstance(resource, platform.frictionless_resources.Extractable):
        note = f'Resource with data type "{resource.datatype}" is not extractable'
        raise FrictionlessException(note)
    return resource.extract(
        name=name, filter=filter, process=process, limit_rows=limit_rows
    )
