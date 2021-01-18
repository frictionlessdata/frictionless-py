from .. import helpers
from ..report import Report
from ..package import Package
from ..inquiry import Inquiry, InquiryTask
from ..exception import FrictionlessException
from .inquiry import validate_inquiry


@Report.from_validate
def validate_package(source, noinfer=False, nolookup=False, parallel=False, **options):
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
        parallel? (bool): enable multiprocessing
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
    inquiry = Inquiry(tasks=[])
    for resource in package.resources:
        # TODO: shall we also validate non-tabular files?
        if resource.profile == "tabular-data-resource":
            inquiry.tasks.append(
                InquiryTask(
                    source=resource,
                    basepath=resource.basepath,
                    noinfer=noinfer,
                )
            )

    # Validate inquiry
    report = validate_inquiry(inquiry, parallel=parallel)

    # Return report
    return Report(time=timer.time, errors=report["errors"], tasks=report["tasks"])
