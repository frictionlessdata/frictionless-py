import warnings
from typing import TYPE_CHECKING
from ..report import Report
from ..inquiry import Inquiry, InquiryTask
from ..exception import FrictionlessException
from .. import helpers

if TYPE_CHECKING:
    from .package import Package


# TODO: move exception catching to high-level validate?
@Report.from_validate
def validate(
    package: "Package",
    resource_name=None,
    original=False,
    parallel=False,
    **options,
):
    """Validate package

    Parameters:
        source (dict|str): a package descriptor
        resource_name (str): validate only selected resource
        original? (bool): validate metadata as it is (without inferring)
        parallel? (bool): enable multiprocessing
        **options (dict): resource validateion options

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Validate resource
    if resource_name:
        resource = package.get_resource(resource_name)
        return resource.validate()

    # Prepare package
    try:
        package_stats = []
        for resource in package.resources:
            package_stats.append({key: val for key, val in resource.stats.items() if val})
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Validate metadata
    metadata_errors = []
    for error in package.metadata_errors:
        if error.code == "package-error":
            metadata_errors.append(error)
        if metadata_errors:
            return Report(time=timer.time, errors=metadata_errors, tasks=[])

    # Validate sequentially
    if not parallel:
        tasks = []
        errors = []
        for resource, stats in zip(package.resources, package_stats):
            resource.stats = stats
            report = resource.validate(original=original, **options)
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
