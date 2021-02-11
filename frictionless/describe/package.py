from ..package import Package


def describe_package(source, *, expand=False, stats=False, **options):
    """Describe the given source as a package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_package`

    Parameters:
        source (any): data source
        expand? (bool): if `True` it will expand the metadata
        stats? (bool): if `True` infer resource's stats
        **options (dict): Package constructor options

    Returns:
        Package: data package

    """
    package = Package(source, **options)
    package.infer(stats=stats)
    if expand:
        package.expand()
    return package
