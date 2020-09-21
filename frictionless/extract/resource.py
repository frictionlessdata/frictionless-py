from ..resource import Resource


def extract_resource(source, *, process=None):
    """Extract resource rows into memory

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_resource`

    Parameters:
        source (dict|str): data resource descriptor
        process? (func): a row processor function

    Returns:
        Row[]: an array of rows

    """

    # Create resource
    resource = Resource(source)

    # Extract resource
    if process:
        result = []
        for row in resource.read_row_stream():
            result.append(process(row))
        return result
    return resource.read_rows()
