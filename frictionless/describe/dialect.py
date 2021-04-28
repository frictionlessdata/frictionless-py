from .resource import describe_resource


def describe_dialect(source=None, **options):
    """Describe the given source as a dialect

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_dialect`

    Parameters:
        source (any): data source
        **options (dict): describe resource options

    Returns:
        Dialect: file dialect
    """
    resource = describe_resource(source, **options)
    return resource.dialect
