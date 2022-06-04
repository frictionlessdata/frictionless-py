from importlib import import_module


def describe(source=None, expand: bool = False, **options):
    """Describe the given source as a schema

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        **options (dict): describe resource options

    Returns:
        Schema: table schema
    """
    frictionless = import_module("frictionless")
    resource = frictionless.Resource.describe(source, **options)
    schema = resource.schema
    if expand:
        schema.expand()
    return schema
