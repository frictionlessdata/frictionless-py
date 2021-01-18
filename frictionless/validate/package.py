from .. import helpers
from ..report import Report
from ..package import Package
from ..inquiry import Inquiry
from ..exception import FrictionlessException
from .inquiry import validate_inquiry


@Report.from_validate
def validate_package(source, noinfer=False, nolookup=False, nopool=False, **options):
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
        nopool? (bool): disable multiprocessing
        **options (dict): Package constructor options

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Create package
    try:
        native = isinstance(source, Package)
        package = source.to_copy() if native else Package(source, **options)
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Prepare package
    if not noinfer:
        package.infer()

    if package.metadata_errors:
        return Report(time=timer.time, errors=package.metadata_errors, tasks=[])

    # Prepare inquiry
    descriptor = {"tasks": []}
    for resource in package.resources:
        if resource.profile == "tabular-data-resource":
            descriptor["tasks"].append(
                helpers.create_descriptor(
                    source=resource,
                    basepath=resource.basepath,
                    noinfer=noinfer,
                )
            )

    # Validate inquiry
    inquiry = Inquiry(descriptor)
    report = validate_inquiry(inquiry, nopool=nopool)

    # Return report
    return Report(time=timer.time, errors=report["errors"], tasks=report["tasks"])
