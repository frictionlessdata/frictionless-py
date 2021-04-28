from ..resource import Resource


def describe_resource(source=None, *, expand=False, stats=False, **options):
    """Describe the given source as a resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_resource`

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        stats? (bool): if `True` infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """
    resource = Resource(source, **options)
    resource.infer(stats=stats)
    if expand:
        resource.expand()
    return resource
