from .. import helpers
from ..report import Report
from ..package import Package
from ..inquiry import Inquiry
from .inquiry import validate_inquiry
from .. import exceptions


@Report.from_validate
def validate_package(
    source, basepath=None, trusted=False, noinfer=False, nolookup=False, **options
):
    """Validate package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_package`

    Parameters:
        source (dict|str): a package descriptor
        basepath? (str): package basepath
        trusted? (bool): don't raise an exception on unsafe paths
        noinfer? (bool): don't call `package.infer`
        nolookup? (bool): don't read lookup tables skipping integrity checks
        **options (dict): options for every extracted table

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Create package
    try:
        package = Package(source, basepath=basepath, trusted=trusted)
    except exceptions.FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tables=[])

    # Prepare package
    if not noinfer:
        package.infer(only_sample=True)

    if package.metadata_errors:
        return Report(time=timer.time, errors=package.metadata_errors, tables=[])

    # Prepare inquiry
    descriptor = {"tasks": []}
    for resource in package.resources:
        if resource.profile == "tabular-data-resource":
            lookup = None if nolookup else resource.read_lookup()
            descriptor["tasks"].append(
                helpers.create_descriptor(
                    **options,
                    source=resource,
                    basepath=resource.basepath,
                    noinfer=noinfer,
                    lookup=lookup,
                )
            )

    # Validate inquiry
    inquiry = Inquiry(descriptor)
    report = validate_inquiry(inquiry)

    # Return report
    return Report(time=timer.time, errors=report["errors"], tables=report["tables"])
