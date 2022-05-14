from importlib import import_module


def describe(source=None, **options):
    """Describe the given source as a schema

    Parameters:
        source (any): data source
        **options (dict): describe resource options

    Returns:
        Schema: table schema
    """
    frictionless = import_module("frictionless")
    resource = frictionless.Resource.describe(source, **options)
    return resource.schema
