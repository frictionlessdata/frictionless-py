from ..resource import Resource


def describe_schema(source, *, expand=False, **options):
    """Describe the given source as a schema

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_schema`

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        **options (dict): Resource constructor options

    Returns:
        Schema: table schema
    """
    resource = Resource(source, **options)
    resource.infer()
    schema = resource.schema
    if expand:
        schema.expand()
    return schema
