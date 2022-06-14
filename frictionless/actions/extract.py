from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from ..system import system

if TYPE_CHECKING:
    from ..interfaces import FilterFunction, ProcessFunction


def extract(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    filter: Optional[FilterFunction] = None,
    process: Optional[ProcessFunction] = None,
    stream: bool = False,
    **options,
):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract`

    Parameters:
        source (dict|str): data source
        type (str): source type - package of resource (default: infer)
        filter? (bool): a row filter function
        process? (func): a row processor function
        stream? (bool): return a row stream(s) instead of loading into memory
        **options (dict): options for the underlaying function

    Returns:
        Row[]|{path: Row[]}: rows in a form depending on the source type
    """

    # Infer type
    if not type:
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"

    # Extract source
    if type == "package":
        if not isinstance(source, Package):
            source = Package(source, **options)
        return source.extract(filter=filter, process=process, stream=stream)
    elif type == "resource":
        if not isinstance(source, Resource):
            source = Resource(source, **options)
        return source.extract(filter=filter, process=process, stream=stream)

    # Not supported
    raise FrictionlessException(f"Not supported extract type: {type}")
