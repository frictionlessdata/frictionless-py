from ..package import Package


def extract_package(source=None, *, process=None, stream=False, **options):
    """Extract package rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_package`

    Parameters:
        source (dict|str): data resource descriptor
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory
        **options (dict): Package constructor options

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """
    result = {}
    native = isinstance(source, Package)
    package = source.to_copy() if native else Package(source, **options)
    for number, resource in enumerate(package.resources, start=1):
        key = resource.fullpath if not resource.memory else f"memory{number}"
        data = read_row_stream(resource)
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
