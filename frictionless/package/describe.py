from importlib import import_module


# TODO: rebase from source to path/glob?
def describe(source=None, *, expand=False, stats=False, **options):
    """Describe the given source as a package

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        stats? (bool): if `True` infer resource's stats
        **options (dict): Package constructor options

    Returns:
        Package: data package

    """
    frictionless = import_module("frictionless")
    package = frictionless.Package(source, **options)
    package.infer(stats=stats)
    if expand:
        package.expand()
    return package
