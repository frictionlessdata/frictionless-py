from .. import helpers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .package import Package


def extract(package: "Package", *, process=None, stream=False, valid=None):
    """Extract package rows

    Parameters:
        package (dict|str): data resource descriptor
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory
        valid? (bool): returns valid rows only if true and viceversa

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """
    result = {}
    row_options = helpers.remove_non_values(dict(valid=valid))
    for number, resource in enumerate(package.resources, start=1):
        key = resource.fullpath if not resource.memory else f"memory{number}"
        data = read_row_stream(resource, **row_options)
        data = (process(row) for row in data) if process else data
        result[key] = data if stream else list(data)
    return result


# Internal


def read_row_stream(resource, **options):
    with resource:
        for row in resource.row_stream:
            if "valid" in options:
                if options["valid"] != row.valid:
                    continue
            yield row
