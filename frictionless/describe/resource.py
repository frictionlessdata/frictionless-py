from ..resource import Resource


def describe_resource(source, *, expand=False, nostats=False, **options):
    """Describe the given source as a resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_resource`

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        nostats? (bool): if `True` it not infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """
    resource = Resource(source, trusted=True, **options)
    resource.infer(stats=not nostats)
    if expand:
        resource.expand()
    return resource
