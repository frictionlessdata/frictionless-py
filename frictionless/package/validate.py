import warnings
from typing import TYPE_CHECKING, Optional, List
from ..check import Check
from ..report import Report
from ..checklist import Checklist
from ..inquiry import Inquiry, InquiryTask
from ..exception import FrictionlessException
from .. import helpers

if TYPE_CHECKING:
    from .package import Package


def validate(
    package: "Package",
    checklist: Optional[Checklist] = None,
):
    """Validate package

    Parameters:
        checklist? (checklist): a Checklist object
        checks? (list): a list of checks

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Prepare package
    try:
        package_stats = []
        for resource in package.resources:  # type: ignore
            package_stats.append({key: val for key, val in resource.stats.items() if val})
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Prepare checklist
    checklist = checklist or Checklist()
    if not checklist.metadata_valid:
        return Report(errors=checklist.metadata_errors, time=timer.time)

    # Validate metadata
    metadata_errors = []
    for error in package.metadata_errors:
        if error.code == "package-error":
            metadata_errors.append(error)
        if metadata_errors:
            return Report(time=timer.time, errors=metadata_errors, tasks=[])

    # Validate sequentially
    if not checklist.allow_parallel:
        tasks = []
        errors = []
        for resource, stats in zip(package.resources, package_stats):  # type: ignore
            resource.stats = stats
            report = resource.validate(checklist)
            tasks.extend(report.tasks)
            errors.extend(report.errors)
        return Report(time=timer.time, errors=errors, tasks=tasks)

    # TODO: don't use inquiry for it (move code here)
    # Validate in-parallel
    else:
        inquiry = Inquiry(tasks=[])
        for resource, stats in zip(package.resources, package_stats):  # type: ignore
            for fk in resource.schema.foreign_keys:
                # TODO: don't do in parallel if there are FKs!!!
                if fk["reference"]["resource"]:
                    message = "Foreign keys validation is ignored in the parallel mode"
                    warnings.warn(message, UserWarning)
                    break
            resource.stats = stats
            inquiry.tasks.append(
                InquiryTask(
                    source=resource,
                    basepath=resource.basepath,
                    original=checklist.keep_original,
                )
            )
        return inquiry.run(parallel=checklist.allow_parallel)
