from .. import helpers
from ..report import Report
from ..resource import Resource
from ..exception import FrictionlessException
from .table import validate_table


@Report.from_validate
def validate_resource(
    source, basepath="", trusted=False, noinfer=False, lookup=None, **options
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
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tables=[])

    # Prepare resource
    if not noinfer:
        resource.infer()
    if resource.metadata_errors:
        return Report(time=timer.time, errors=resource.metadata_errors, tables=[])

    # Prepare table
    # TODO: review lookup preparation
    if lookup is None:
        with resource.to_copy() as rescopy:
            lookup = rescopy.lookup

    # Validate table
    report = validate_table(
        source=resource.data if resource.memory else resource.fullpath,
        scheme=resource.scheme,
        format=resource.format,
        hashing=resource.hashing,
        encoding=resource.encoding,
        innerpath=resource.innerpath,
        compression=resource.compression,
        dialect=resource.dialect,
        # TODO: review (see issue 615)
        schema=resource.schema.to_dict(),
        lookup=lookup,
        # TODO: review
        checksum=resource.stats,
        **options,
    )

    # Return report
    return Report(time=timer.time, errors=report["errors"], tables=report["tables"])
