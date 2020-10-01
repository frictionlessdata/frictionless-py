from collections import OrderedDict
from ..package import Package


def extract_package(
    source,
    *,
    basepath=None,
    onerror="ignore",
    trusted=False,
    process=None,
    stream=False,
):
    """Extract package rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_package`

    Parameters:
        source (dict|str): data resource descriptor
        basepath? (str): package basepath
        onerror? (ignore|warn|raise): behaviour on errors
        trusted? (bool): don't raise an exception on unsafe paths
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """

    # Create package
    package = Package(source, basepath=basepath, onerror=onerror, trusted=trusted)

    # Extract package
    result = OrderedDict()
    for number, resource in enumerate(package.resources, start=1):
        key = resource.fullpath if not resource.inline else f"memory{number}"
        data = resource.read_row_stream()
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result
