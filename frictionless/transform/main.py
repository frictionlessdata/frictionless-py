from .package import transform_package


def transform(source):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform`

    Parameters:
        source (any): data source
    """
    return transform_package(source)
