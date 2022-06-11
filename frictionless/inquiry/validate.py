from multiprocessing import Pool
from typing import TYPE_CHECKING
from .task import InquiryTask
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
        return Report.from_validation(time=timer.time, errors=inquiry.metadata_errors)

    # Validate sequentially
    if not parallel:
        for task in inquiry.tasks:
            report = task.run()
            reports.append(report)

    # Validate in-parallel
    else:
        with Pool() as pool:
            task_descriptors = [task.to_dict() for task in inquiry.tasks]
            report_descriptors = pool.map(run_task_in_parallel, task_descriptors)
            for report_descriptor in report_descriptors:
                reports.append(Report.from_descriptor(report_descriptor))

    # Return report
    tasks = []
    errors = []
    for report in reports:
        tasks.extend(report.tasks)
        errors.extend(report.errors)
    return Report.from_validation(time=timer.time, errors=errors)


# Internal


def run_task_in_parallel(task_descriptor):
    task = InquiryTask.from_descriptor(task_descriptor)
    report = task.run()  # type: ignore
    report_descriptor = report.to_dict()
    return report_descriptor
