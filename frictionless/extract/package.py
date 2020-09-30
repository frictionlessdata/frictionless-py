from collections import OrderedDict
from ..package import Package


def extract_package(
    source,
    *,
    basepath=None,
    on_unsafe="raise",
    on_error="ignore",
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
        on_unsafe? (ignore|warn|raise): behaviour on unsafe paths
        on_error? (ignore|warn|raise): behaviour on errors
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """

    # Create package
    package = Package(source, basepath=basepath, on_unsafe=on_unsafe, on_error=on_error)

    # Extract package
    result = OrderedDict()
    for number, resource in enumerate(package.resources, start=1):
        key = resource.fullpath if not resource.inline else f"memory{number}"
        data = resource.read_row_stream()
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result
