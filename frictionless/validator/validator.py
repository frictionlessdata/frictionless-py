from __future__ import annotations

from multiprocessing import Pool
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .. import helpers, settings
from ..checklist import Checklist
from ..exception import FrictionlessException
from ..platform import platform
from ..report import Report

if TYPE_CHECKING:
    from .. import types
    from ..error import Error
    from ..package import Package
    from ..resource import Resource


class Validator:
    # Package

    def validate_package(
        self,
        package: Package,
        *,
        checklist: Optional[Checklist] = None,
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
                    checklist=checklist,
                    limit_errors=limit_errors,
                    limit_rows=limit_rows,
                )
                reports.append(report)

        # Validate parallel
        else:
            with Pool() as pool:
                options_pool: List[Dict[str, Any]] = []
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

    # Resource

    def validate_resource(
        self,
        resource: Resource,
        *,
        checklist: Optional[Checklist] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
        limit_rows: Optional[int] = None,
        on_row: Optional[types.ICallbackFunction] = None,
    ):
        # Create state
        partial = False
        timer = helpers.Timer()
        labels: List[str] = []
        errors: List[Error] = []
        warnings: List[str] = []

        # Prepare checklist
        checklist = checklist or Checklist()
        checks = checklist.connect(resource)

        # Validate metadata
        try:
            resource.to_descriptor(validate=True)
        except FrictionlessException as exception:
            return Report.from_validation_task(
                resource, time=timer.time, errors=exception.to_errors()
            )

        # TODO: remove in next version
        # Ignore not-supported hashings
        if resource.hash:
            algorithm, _ = helpers.parse_resource_hash_v1(resource.hash)
            if algorithm not in ["md5", "sha256"]:
                warning = "hash is ignored; supported algorithms: md5/sha256"
                warnings.append(warning)

        # Prepare resource
        if resource.closed:
            try:
                resource.open()
            except FrictionlessException as exception:
                resource.close()
                return Report.from_validation_task(
                    resource, time=timer.time, errors=exception.to_errors()
                )

        # Validate data
        with resource:
            # Validate start
            for index, check in enumerate(checks):
                for error in check.validate_start():
                    if error.type == "check-error":
                        del checks[index]
                    if checklist.match(error):
                        errors.append(error)

            # Validate file
            if not isinstance(resource, platform.frictionless_resources.TableResource):
                if resource.hash is not None or resource.bytes is not None:
                    helpers.pass_through(resource.byte_stream)

            # Validate table
            else:
                row_count = 0
                labels = resource.labels
                while True:
                    row_count += 1

                    # Emit row
                    try:
                        row = next(resource.row_stream)  # type: ignore
                    except FrictionlessException as exception:
                        errors.append(exception.error)
                        continue
                    except StopIteration:
                        break

                    # Validate row
                    for check in checks:
                        for error in check.validate_row(row):
                            if checklist.match(error):
                                errors.append(error)

                    # Callback row
                    if on_row:
                        on_row(row)

                    # Limit rows
                    if limit_rows:
                        if row_count >= limit_rows:
                            warning = f"reached row limit: {limit_rows}"
                            warnings.append(warning)
                            partial = True
                            break

                    # Limit errors
                    if limit_errors:
                        if len(errors) >= limit_errors:
                            errors = errors[:limit_errors]
                            warning = f"reached error limit: {limit_errors}"
                            warnings.append(warning)
                            partial = True
                            break

            # Validate end
            if not partial:
                for check in checks:
                    for error in check.validate_end():
                        if checklist.match(error):
                            errors.append(error)

        # Return report
        return Report.from_validation_task(
            resource, time=timer.time, labels=labels, errors=errors, warnings=warnings
        )


# Internal


def validate_parallel(options: types.IDescriptor) -> types.IDescriptor:
    from ..resource import Resource  # Local import avoids circular import

    resource_options = options["resource"]
    validate_options = options["validate"]
    resource = Resource.from_descriptor(**resource_options)
    report = resource.validate(**validate_options)
    return report.to_descriptor()
