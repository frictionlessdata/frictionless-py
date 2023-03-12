from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Union
from ..exception import FrictionlessException
from ..platform import platform
from ..resource import Resource

if TYPE_CHECKING:
    from ..dialect import Dialect


def convert(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    # Convert
    to_path: str,
    to_format: Optional[str] = None,
    to_dialect: Optional[Union[Dialect, str]] = None,
    **options,
) -> str:
    """Convert data source"""
    resource = Resource(source, name=name or "", datatype=type or "", **options)
    if not isinstance(resource, platform.frictionless_resources.Convertible):
        note = f'Resource with data type "{resource.datatype}" is not convertible'
        raise FrictionlessException(note)
    return resource.convert(to_path=to_path, to_format=to_format, to_dialect=to_dialect)
