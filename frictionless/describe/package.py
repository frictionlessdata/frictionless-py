from ..package import Package


# TODO: support only_sample
def describe_package(source, *, hashing=None, basepath=None, expand=False):
    """Describe the given source as a package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_package`

    Parameters:
        source (any): data source
        hashing? (str): a hashing algorithm for resources
        basepath? (str): package basepath
        expand? (bool): if `True` it will expand the metadata

    Returns:
        Package: data package

    """

    # Infer package
    package = Package(hashing=hashing, basepath=basepath, trusted=True)
    package.infer(source)

    # Expand package
    if expand:
        package.expand()

    return package
