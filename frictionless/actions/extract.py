from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Union
from ..detector import Detector
from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from .. import helpers

if TYPE_CHECKING:
    from ..schema import Schema
    from ..dialect import Dialect
    from ..interfaces import IFilterFunction, IProcessFunction


def extract(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    dialect: Optional[Union[Dialect, str]] = None,
    schema: Optional[Union[Schema, str]] = None,
    limit_rows: Optional[int] = None,
    process: Optional[IProcessFunction] = None,
    filter: Optional[IFilterFunction] = None,
    stream: bool = False,
    resource_name: Optional[str] = None,
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
    if resource_name:
        type = "resource"
    if not type:
        type = getattr(source, "metadata_type", None)
    if not type:
        type = Detector.detect_descriptor(source)
    if not type:
        type = "resource"
        if helpers.is_expandable_source(source):
            type = "package"

    # Extract resource
    if type == "resource":
        if resource_name:
            package = source
            if not isinstance(package, Package):
                package = Package.from_options(source, **options)
            resource = package.get_resource(resource_name)
        else:
            resource = source
            if not isinstance(resource, Resource):
                resource = Resource.from_options(
                    source,
                    type="table",
                    dialect=dialect,
                    schema=schema,
                    **options,
                )
        return resource.extract(
            limit_rows=limit_rows,
            process=process,
            filter=filter,
            stream=stream,
        )

    # Extract package
    if type == "package":
        package = source
        if not isinstance(package, Package):
            package = Package.from_options(source, **options)
        return package.extract(
            limit_rows=limit_rows,
            process=process,
            filter=filter,
            stream=stream,
        )

    # Not supported
    raise FrictionlessException(f"Not supported extract type: {type}")
