from ..resource import Resource


def extract_resource(source, *, process=None, stream=False, **options):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_resource`

    Parameters:
        source (dict|str): data resource descriptor
        process? (func): a row processor function
        **options (dict): Resource constructor options

    Returns:
        Row[]: an array/stream of rows

    """
    native = isinstance(source, Resource)
    resource = source.to_copy() if native else Resource(source, **options)
    data = read_row_stream(resource)
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row
