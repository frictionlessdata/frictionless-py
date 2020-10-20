from ..resource import Resource
from .package import transform_package
from .resource import transform_resource


def transform(source, **options):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform`

    Parameters:
        source (any): data source
    """
    if isinstance(source, Resource):
        return transform_resource(source, **options)
    return transform_package(source)
