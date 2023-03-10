from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union
from ..platform import platform
from ..resource import Resource
from ..package import Package

if TYPE_CHECKING:
    from ..dialect import Dialect
    from ..schema import Schema


def describe(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    stats: bool = False,
    **options,
) -> Union[Package, Resource, Dialect, Schema]:
    """Describe the data source

    Parameters:
        source: data source
        type: source type - `dialect`, `schema`, `resource` or `package` (default: infer)
        stats? (bool): if `True` infer resource's stats
        **options (dict): options for the detecting Resource class

    Returns:
        Metadata: described metadata e.g. a Table Schema
    """
    resources = platform.frictionless_resources

    # Create resource
    resource = Resource(
        source,
        name=name or "",
        packagify=type == "package",
        **options,
    )

    # Infer package
    if isinstance(resource, resources.PackageResource):
        package = resource.read_metadata()
        package.infer(stats=stats)
        if name is not None:
            return package.get_resource(name)
        return package
    elif type == "package":
        return Package(resources=[resource])

    # Infer resource
    resource.infer(stats=stats)
    if type == "dialect":
        return resource.dialect
    if type == "schema":
        return resource.schema
    return resource
