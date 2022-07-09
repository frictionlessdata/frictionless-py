from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from ..detector import Detector
from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction


def extract(
    source: Any,
    *,
    type: Optional[str] = None,
    limit_rows: Optional[int] = None,
    process: Optional[IProcessFunction] = None,
    filter: Optional[IFilterFunction] = None,
    stream: bool = False,
    **options,
):
    """Extract resource rows

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

    # Detect type
    if not type:
        type = Detector.detect_descriptor(source)
        if not type:
            type = "resource"
            if helpers.is_expandable_source(source):
                type = "package"

    # Extract package
    if type == "package":
        package = source
        if not isinstance(package, Package):
            package = Package.from_options(package, **options)
        return package.extract(
            limit_rows=limit_rows,
            process=process,
            filter=filter,
            stream=stream,
        )

    # Extract resource
    elif type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource.from_options(resource, **options)
        return resource.extract(
            limit_rows=limit_rows,
            process=process,
            filter=filter,
            stream=stream,
        )

    # Not supported
    raise FrictionlessException(f"Not supported extract type: {type}")
