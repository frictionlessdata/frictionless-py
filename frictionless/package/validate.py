from __future__ import annotations
from multiprocessing import Pool
from typing import TYPE_CHECKING, Optional, List
from ..exception import FrictionlessException
from ..checklist import Checklist
from ..resource import Resource
from ..report import Report
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor
    from ..package import Package


def validate(
    package: Package,
    checklist: Optional[Checklist] = None,
    *,
    name: Optional[str] = None,
    parallel: bool = False,
    limit_rows: Optional[int] = None,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
):
    # Create state
    timer = helpers.Timer()
    reports: List[Report] = []
    resources = package.resources if name is None else [package.get_resource(name)]
    with_fks = any(res.schema and res.schema.foreign_keys for res in resources)

    # Prepare checklist
    checklist = checklist or Checklist()

    # Validate metadata
    try:
        package.to_descriptor(validate=True)
    except FrictionlessException as exception:
        return Report.from_validation(time=timer.time, errors=exception.to_errors())

    # Validate sequential
    if not parallel or with_fks:
        for resource in resources:
            report = resource.validate(
                limit_errors=limit_errors,
                limit_rows=limit_rows,
            )
            reports.append(report)

    # Validate parallel
    else:
        with Pool() as pool:
            options_pool: List[dict] = []
            for resource in resources:
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
