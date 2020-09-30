from ..package import Package


def describe_package(source, *, basepath=None, on_unsafe="raise", expand=False):
    """Describe the given source as a package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_package`

    Parameters:
        source (any): data source
        basepath? (str): package basepath
        on_unsafe? (ignore|warn|raise): behaviour on unsafe paths
        expand? (bool): if `True` it will expand the metadata

    Returns:
        Package: data package

    """

    # Infer package
    package = Package(basepath=basepath, on_unsafe=on_unsafe)
    package.infer(source)

    # Expand package
    if expand:
        package.expand()

    return package
