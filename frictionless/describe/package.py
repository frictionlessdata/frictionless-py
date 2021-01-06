from ..package import Package


def describe_package(source, *, expand=False, nostats=False, **options):
    """Describe the given source as a package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_package`

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        nostats? (bool): if `True` it not infer resource's stats
        **options (dict): Package constructor options

    Returns:
        Package: data package

    """
    package = Package(source, trusted=True, **options)
    package.infer(stats=not nostats)
    if expand:
        package.expand()
    return package
