import builtins
import warnings
from ..resource import Resource
from ..package import Package
from ..exception import FrictionlessException
from ..system import system
from .. import errors


def extract(
    source=None, *, type=None, process=None, stream=False, filter=None, **options
):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract`

    Parameters:
        source (dict|str): data source
        type (str): source type - package of resource (default: infer)
        process? (func): a row processor function
        stream? (bool): return a row stream(s) instead of loading into memory
        filter? (bool): row processor function to filter valid/invalid rows
        **options (dict): options for the underlaying function

    Returns:
        Row[]|{path: Row[]}: rows in a form depending on the source type
    """
    if not type:
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"
    extract = globals().get("extract_%s" % type, None)
    if extract is None:
        note = f"Not supported extract type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    return extract(
        source,
        process=process,
        stream=stream,
        deprecate=False,
        filter=filter,
        **options,
    )


def extract_package(
    source=None,
    *,
    process=None,
    stream=False,
    deprecate=True,
    filter=None,
    **options,
):
    """Extract package rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_package`

    Parameters:
        source (dict|str): data resource descriptor
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory
        deprecate? (bool): flag to check if the function is deprecated
        filter? (bool): row processor function to filter valid/invalid rows
        **options (dict): Package constructor options

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """
    if deprecate:
        message = 'Function "extract_package" is deprecated (use "package.extract").'
        warnings.warn(message, UserWarning)
    result = {}
    native = isinstance(source, Package)
    package = source.to_copy() if native else Package(source, **options)
    for number, resource in enumerate(package.resources, start=1):
        key = resource.fullpath if not resource.memory else f"memory{number}"
        data = read_row_stream(resource)
        data = builtins.filter(filter, data) if filter else data
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result


def extract_resource(
    source=None,
    *,
    process=None,
    stream=False,
    deprecate=True,
    filter=None,
    **options,
):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_resource`

    Parameters:
        source (any|Resource): data resource
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory
        deprecate? (bool): flag to check if the function is deprecated
        filter? (bool): row processor function to filter valid/invalid rows
        **options (dict): Resource constructor options

    Returns:
        Row[]: an array/stream of rows

    """
    if deprecate:
        message = 'Function "extract_resource" is deprecated (use "resource.extract").'
        warnings.warn(message, UserWarning)
    native = isinstance(source, Resource)
    resource = source.to_copy() if native else Resource(source, **options)
    data = read_row_stream(resource)
    data = builtins.filter(filter, data) if filter else data
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
