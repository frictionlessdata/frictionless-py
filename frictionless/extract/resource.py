from ..resource import Resource


def extract_resource(
    source,
    *,
    basepath=None,
    onerror="ignore",
    trusted=False,
    process=None,
    stream=False,
):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_resource`

    Parameters:
        source (dict|str): data resource descriptor
        basepath? (str): package basepath
        onerror? (ignore|warn|raise): behaviour on errors
        trusted? (bool): don't raise an exception on unsafe paths
        process? (func): a row processor function

    Returns:
        Row[]: an array/stream of rows

    """

    # Create resource
    resource = Resource(source, basepath=basepath, onerror=onerror, trusted=trusted)

    # Extract resource
    data = read_row_stream(resource)
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
