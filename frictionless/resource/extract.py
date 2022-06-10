from .. import helpers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .resource import Resource


def extract(resource: "Resource", *, process=None, stream=False, valid=None):
    """Extract resource rows

    Parameters:
        resource (dict|str): resource descriptor
        process? (func): a row processor function
        stream? (bool): whether to stream data
        valid? (bool): returns valid rows only if true and viceversa

    Returns:
        Row[]: an array/stream of rows

    """
    row_options = helpers.remove_non_values(dict(valid=valid))
    data = read_row_stream(resource, **row_options)
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(resource, **options):
    with resource:
        for row in resource.row_stream:
            if "valid" in options:
                if options["valid"] != row.valid:
                    continue
            yield row
