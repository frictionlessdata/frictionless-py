from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from ..system import system
from .. import errors


def describe(source=None, *, type=None, **options):
    """Describe the data source

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe`

    Parameters:
        source (any): data source
        type (str): source type - `schema`, `resource` or `package` (default: infer)
        **options (dict): options for the underlaying describe function

    Returns:
        Package|Resource|Schema: metadata
    """
    if not type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        type = "package" if file.multipart else "resource"
    describe = globals().get("describe_%s" % type, None)
    if describe is None:
        note = f"Not supported describe type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    return describe(source, **options)


def describe_dialect(source=None, **options):
    """Describe the given source as a dialect

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_dialect`

    Parameters:
        source (any): data source
        **options (dict): describe resource options

    Returns:
        Dialect: file dialect
    """
    resource = describe_resource(source, **options)
    return resource.dialect


def describe_package(source=None, *, expand=False, stats=False, **options):
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


def describe_schema(source=None, **options):
    """Describe the given source as a schema

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_schema`

    Parameters:
        source (any): data source
        **options (dict): describe resource options

    Returns:
        Schema: table schema
    """
    resource = describe_resource(source, **options)
    return resource.schema
