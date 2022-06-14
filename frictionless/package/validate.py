from __future__ import annotations
from multiprocessing import Pool
from typing import TYPE_CHECKING, Optional, List
from ..checklist import Checklist
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .package import Package
    from ..resource import Resource


def validate(
    package: "Package",
    checklist: Optional[Checklist] = None,
    *,
    original: bool = False,
    parallel: bool = False,
):
    """Validate package

    Parameters:
        checklist? (checklist): a Checklist object
        parallel? (bool): run in parallel if possible

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()
    reports: List[Report] = []
    with_fks = any(resource.schema.foreign_keys for resource in package.resources)  # type: ignore

    # Prepare checklist
    checklist = checklist or Checklist()
    if not checklist.metadata_valid:
        errors = checklist.metadata_errors
        return Report.from_validation(time=timer.time, errors=errors)

    # Validate metadata
    metadata_errors = []
    for error in package.metadata_errors:
        if error.code == "package-error":
            metadata_errors.append(error)
    if metadata_errors:
        return Report.from_validation(time=timer.time, errors=metadata_errors)

    # Validate sequential
    if not parallel or with_fks:
        for resource in package.resources:  # type: ignore
            report = validate_sequential(resource, original=original)
            reports.append(report)

    # Validate parallel
    else:
        with Pool() as pool:
            resource_descriptors: List[dict] = []
            for resource in package.resources:  # type: ignore
                descriptor = resource.to_dict()
                descriptor["basepath"] = resource.basepath
                descriptor["trusted"] = resource.trusted
                descriptor["original"] = original
                resource_descriptors.append(descriptor)
            report_descriptors = pool.map(validate_parallel, resource_descriptors)
            for report_descriptor in report_descriptors:
                reports.append(Report.from_descriptor(report_descriptor))  # type: ignore

    # Return report
    return Report.from_validation_reports(
        time=timer.time,
        reports=reports,
    )


# Internal


def validate_sequential(resource: Resource, *, original=False) -> Report:
    return resource.validate(original=original)


# TODO: rebase on from/to_descriptor
def validate_parallel(descriptor: dict) -> dict:
    basepath = descriptor.pop("basepath")
    trusted = descriptor.pop("trusted")
    original = descriptor.pop("original")
    resource = Resource(descriptor=descriptor, basepath=basepath, trusted=trusted)
    report = resource.validate(original=original)
    return report.to_dict()  # type: ignore
