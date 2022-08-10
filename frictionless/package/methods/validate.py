from __future__ import annotations
from multiprocessing import Pool
from typing import TYPE_CHECKING, Optional, List
from ...exception import FrictionlessException
from ...checklist import Checklist
from ...resource import Resource
from ...report import Report
from ... import settings
from ... import helpers

if TYPE_CHECKING:
    from ...interfaces import IDescriptor
    from ..package import Package


def validate(
    self: Package,
    checklist: Optional[Checklist] = None,
    *,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
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
    with_fks = any(
        resource.has_schema and resource.schema.foreign_keys
        for resource in self.resources
    )

    # Prepare checklist
    checklist = checklist or Checklist()

    # Validate metadata
    try:
        self.to_descriptor()
    except FrictionlessException as exception:
        return Report.from_validation(time=timer.time, errors=exception.to_errors())

    # Validate sequential
    if not parallel or with_fks:
        for resource in self.resources:
            report = resource.validate(
                limit_errors=limit_errors,
                limit_rows=limit_rows,
            )
            reports.append(report)

    # Validate parallel
    else:
        with Pool() as pool:
            options_pool: List[dict] = []
            for resource in self.resources:
                options = {}
                options["resource"] = {}
                options["resource"]["descriptor"] = resource.to_descriptor()
                options["resource"]["basepath"] = resource.basepath
                options["validate"] = {}
                options["validate"]["limit_rows"] = limit_rows
                options["validate"]["limit_errors"] = limit_errors
                options_pool.append(options)
            report_descriptors = pool.map(validate_parallel, options_pool)
            for report_descriptor in report_descriptors:
                reports.append(Report.from_descriptor(report_descriptor))

    # Return report
    return Report.from_validation_reports(
        time=timer.time,
        reports=reports,
    )


# Internal


def validate_parallel(options: IDescriptor) -> IDescriptor:
    resource_options = options["resource"]
    validate_options = options["validate"]
    resource = Resource.from_descriptor(**resource_options)
    report = resource.validate(**validate_options)
    return report.to_descriptor()
