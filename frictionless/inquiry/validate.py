from multiprocessing import Pool
from typing import TYPE_CHECKING, cast
from .task import InquiryTask
from ..resource import Resource
from ..package import Package
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .inquiry import Inquiry


def validate(inquiry: "Inquiry", *, parallel=False):
    """Validate inquiry

    Parameters:
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """

    # Create state
    reports = []
    timer = helpers.Timer()

    # Validate inquiry
    if inquiry.metadata_errors:
        errors = inquiry.metadata_errors
        return Report.from_validation(time=timer.time, errors=errors)

    # Validate sequentially
    if not parallel:
        for task in inquiry.tasks:
            report = validate_task(task)
            reports.append(report)

    # Validate in-parallel
    else:
        with Pool() as pool:
            task_descriptors = [task.to_dict() for task in inquiry.tasks]
            report_descriptors = pool.map(validate_task_in_parallel, task_descriptors)
            for report_descriptor in report_descriptors:
                reports.append(Report.from_descriptor(report_descriptor))

    # Return report
    tasks = []
    errors = []
    warnings = []
    for report in reports:
        tasks.extend(report.tasks)
        errors.extend(report.errors)
        warnings.extend(report.warnings)
    return Report.from_validation(
        time=timer.time,
        tasks=tasks,
        errors=errors,
        warnings=warnings,
    )


# Internal


def validate_task(task: InquiryTask) -> Report:

    # Package
    if task.type == "package":
        package = Package(descriptor=task.descriptor)
        report = package.validate(task.checklist)
        return report

    # Resource
    resource = (
        Resource(
            path=task.path,
            scheme=task.scheme,
            format=task.format,
            hashing=task.hashing,
            encoding=task.encoding,
            innerpath=task.innerpath,
            compression=task.compression,
            dialect=task.dialect,
            schema=task.schema,
            # TODO: pass checklist here
        )
        if not task.descriptor
        # TODO: rebase on Resource.from_descriptor
        else Resource(descriptor=task.descriptor)
    )
    report = resource.validate(task.checklist)
    return report


# TODO: rebase on IDescriptor
def validate_task_in_parallel(descriptor: dict) -> dict:
    task = InquiryTask.from_descriptor(descriptor)
    report = validate_task(task)
    # TODO: rebase on report.[to_]descriptor
    return cast(dict, report.to_dict())
