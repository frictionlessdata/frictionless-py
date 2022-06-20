from __future__ import annotations
from multiprocessing import Pool
from importlib import import_module
from typing import TYPE_CHECKING, List
from ..resource import Resource
from ..package import Package
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor
    from .inquiry import Inquiry, InquiryTask


def validate(inquiry: "Inquiry", *, parallel=False):
    """Validate inquiry

    Parameters:
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()
    reports: List[Report] = []

    # Validate inquiry
    if inquiry.metadata_errors:
        errors = inquiry.metadata_errors
        return Report.from_validation(time=timer.time, errors=errors)

    # Validate sequential
    if not parallel:
        for task in inquiry.tasks:
            report = validate_sequential(task)
            reports.append(report)

    # Validate parallel
    else:
        with Pool() as pool:
            task_descriptors = [task.to_descriptor() for task in inquiry.tasks]
            report_descriptors = pool.map(validate_parallel, task_descriptors)
            for report_descriptor in report_descriptors:
                reports.append(Report.from_descriptor(report_descriptor))

    # Return report
    return Report.from_validation_reports(
        time=timer.time,
        reports=reports,
    )


# Internal


def validate_sequential(task: InquiryTask) -> Report:

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


def validate_parallel(descriptor: IDescriptor) -> IDescriptor:
    InquiryTask = import_module("frictionless").InquiryTask
    task = InquiryTask.from_descriptor(descriptor)
    report = validate_sequential(task)
    return report.to_descriptor()
