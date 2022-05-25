from importlib import import_module


# TODO: rebase from source to path/data
def describe(source=None, *, expand=False, stats=False, **options):
    """Describe the given source as a resource

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        stats? (bool): if `True` infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """
    frictionless = import_module("frictionless")
    resource = frictionless.Resource(source, **options)
    resource.infer(stats=stats)
    if expand:
        resource.expand()
    return resource
