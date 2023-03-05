from typing import Any, Optional
from ..platform import platform
from ..resource import Resource


def describe(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    stats: bool = False,
    **options,
):
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
    datatype = ""
    if type:
        datatype = "package" if type == "package" else "resource"
    resource = Resource(source, name=name or "", datatype=datatype, **options)

    # Infer package
    if isinstance(resource, resources.PackageResource):
        package = resource.read_metadata()
        package.infer(stats=stats)
        if name is not None:
            return package.get_resource(name)
        return package

    # Infer resource
    resource.infer(stats=stats)
    if type == "dialect":
        return resource.dialect
    if type == "schema":
        return resource.schema
    return resource
