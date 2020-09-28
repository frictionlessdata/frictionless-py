from ..resource import Resource


def extract_resource(source, *, process=None, stream=False):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_resource`

    Parameters:
        source (dict|str): data resource descriptor
        process? (func): a row processor function

    Returns:
        Row[]: an array/stream of rows

    """

    # Create resource
    resource = Resource(source)

    # Extract resource
    data = resource.read_row_stream()
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)
