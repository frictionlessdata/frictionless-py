from __future__ import annotations
import warnings
from typing import TYPE_CHECKING, Optional, Any
from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from ..system import system
from .. import errors

if TYPE_CHECKING:
    from ..interfaces import ProcessFunction


def extract(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
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

    # Extract data
    if type == "package":
        package = Package(source, **options)
        return package.extract(process=process, stream=stream)
    elif type == "resource":
        resource = Resource(source, **options)
        return resource.extract(process=process, stream=stream)

    # Not supported
    note = f"Not supported extract type: {type}"
    raise FrictionlessException(errors.GeneralError(note=note))
