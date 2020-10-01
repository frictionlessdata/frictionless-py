from .. import helpers
from ..report import Report
from ..resource import Resource
from .table import validate_table
from .. import exceptions


@Report.from_validate
def validate_resource(
    source, basepath=None, trusted=False, noinfer=False, lookup=None, **options
):
    """Validate resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_resource`

    Parameters:
        source (dict|str): a resource descriptor
        basepath? (str): resource basepath
        trusted? (bool): don't raise an exception on unsafe paths
        noinfer? (bool): don't call `resource.infer`
        lookup? (dict): a lookup object
        **options (dict): resource options

    Returns:
        Report: validation report

    """

    # Prepare state
    timer = helpers.Timer()

    # Create resource
    try:
        resource = Resource(source, basepath=basepath, trusted=trusted)
    except exceptions.FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tables=[])

    # Prepare resource
    if not noinfer:
        resource.infer(only_sample=True)
    if resource.metadata_errors:
        return Report(time=timer.time, errors=resource.metadata_errors, tables=[])

    # Prepare table
    if lookup is None:
        lookup = resource.read_lookup()

    # Validate table
    report = validate_table(
        source=resource.source,
        scheme=resource.scheme,
        format=resource.format,
        hashing=resource.hashing,
        encoding=resource.encoding,
        compression=resource.compression,
        compression_path=resource.compression_path,
        dialect=resource.dialect,
        schema=resource.schema,
        lookup=lookup,
        checksum=resource.stats,
        **options,
    )

    # Return report
    return Report(time=timer.time, errors=report["errors"], tables=report["tables"])
