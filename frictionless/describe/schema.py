from .resource import describe_resource


def describe_schema(source=None, **options):
    """Describe the given source as a schema

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_schema`

    Parameters:
        source (any): data source
        **options (dict): describe resource options

    Returns:
        Schema: table schema
    """
    resource = describe_resource(source, **options)
    return resource.schema
