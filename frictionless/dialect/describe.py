from importlib import import_module


def describe(source=None, expand: bool = False, **options):
    """Describe the given source as a dialect

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        **options (dict): describe resource options

    Returns:
        Dialect: table dialect
    """
    frictionless = import_module("frictionless")
    resource = frictionless.Resource.describe(source, **options)
    dialect = resource.dialect
    if expand:
        dialect.expand()
    return dialect
