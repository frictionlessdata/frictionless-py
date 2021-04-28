import inspect
import warnings
from ..report import Report
from ..package import Package
from ..inquiry import Inquiry, InquiryTask
from ..exception import FrictionlessException
from .resource import validate_resource
from .. import helpers


@Report.from_validate
def validate_package(source=None, original=False, parallel=False, **options):
    """Validate package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_package`

    Parameters:
        source (dict|str): a package descriptor
        basepath? (str): package basepath
        trusted? (bool): don't raise an exception on unsafe paths
        original? (bool): don't call `package.infer`
        parallel? (bool): enable multiprocessing
        **options (dict): Package constructor options

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Prepare options
    package_options = {}
    signature = inspect.signature(validate_resource)
    for name, value in options.copy().items():
        param = signature.parameters.get(name)
        if not param or param.kind != param.KEYWORD_ONLY:
            package_options[name] = options.pop(name)

    # Create package
    try:
        native = isinstance(source, Package)
        package = source.to_copy() if native else Package(source, **package_options)
        package_stats = []
        for resource in package.resources:
            package_stats.append({key: val for key, val in resource.stats.items() if val})
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Prepare package
    if not original:
        package.infer()
    if package.metadata_errors:
        return Report(time=timer.time, errors=package.metadata_errors, tasks=[])

    # Validate sequentially
    if not parallel:
        tasks = []
        errors = []
        for resource, stats in zip(package.resources, package_stats):
            resource.stats = stats
            report = validate_resource(resource, original=original, **options)
            tasks.extend(report.tasks)
            errors.extend(report.errors)
        return Report(time=timer.time, errors=errors, tasks=tasks)

    # Validate in-parallel
    else:
        inquiry = Inquiry(tasks=[])
        for resource, stats in zip(package.resources, package_stats):
            for fk in resource.schema.foreign_keys:
                if fk["reference"]["resource"]:
                    message = "Foreign keys validation is ignored in the parallel mode"
                    warnings.warn(message, UserWarning)
                    break
            resource.stats = stats
            inquiry.tasks.append(
                InquiryTask(
                    source=resource,
                    basepath=resource.basepath,
                    original=original,
                    **options,
                )
            )
        return inquiry.run(parallel=parallel)
