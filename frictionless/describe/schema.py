from .resource import describe_resource


def describe_schema(source, **options):
    """Describe schema of the given source

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_schema`

    Parameters:
        source (any): data source
        **options (dict): see `describe_resource` options

    Returns:
        Schema: table schema
    """
    resource = describe_resource(source, **options)
    schema = resource.schema
    return schema
