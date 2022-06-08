from __future__ import annotations
import types
from typing import TYPE_CHECKING, List, Union, Optional
from ..check import Check
from ..system import system
from ..checklist import Checklist
from ..exception import FrictionlessException
from ..errors import GeneralError, TaskError
from ..report import Report, ReportTask
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from .resource import Resource


def validate(
    resource: "Resource",
    checklist: Optional[Checklist] = None,
    *,
    checks: Optional[List[Check]] = None,
):
    """Validate resource

    Parameters:
        checklist? (checklist): a Checklist object
        checks? (list): a list of checks

    Returns:
        Report: validation report
    """

    # Create state
    errors = []
    partial = False
    timer = helpers.Timer()
    original_resource = resource.to_copy()

    # Prepare checklist
    if not checklist:
        checklist = Checklist(checks=checks)
    connected_checks = checklist.connect(resource)
    if not checklist.metadata_valid:
        return Report(errors=checklist.metadata_errors, time=timer.time)

    # Prepare resource
    try:
        resource.open()
    except FrictionlessException as exception:
        resource.close()
        errors = [exception.error]
        return Report.from_task(resource, errors=errors, time=timer.time)

    # Validate metadata
    metadata = original_resource if checklist.keep_original else resource
    if not metadata.metadata_valid:
        errors = metadata.metadata_errors
        return Report.from_task(resource, errors=errors, time=timer.time)

    # Validate data
    with resource:

        # Validate start
        for index, check in enumerate(connected_checks):
            for error in check.validate_start():
                if error.code == "check-error":
                    del connected_checks[index]
                if error.code in checklist.scope:
                    errors.append(error)

        # Validate rows
        if resource.tabular:
            for row in resource.row_stream:  # type: ignore

                # Validate row
                for check in connected_checks:
                    for error in check.validate_row(row):
                        if error.code in checklist.scope:
                            errors.append(error)

                # Limit errors
                if checklist.limit_errors:
                    if len(errors) >= checklist.limit_errors:
                        errors = errors[: checklist.limit_errors]
                        partial = True
                        break

                # Limit memory
                if checklist.limit_memory:
                    if not row.row_number % 100000:
                        memory = helpers.get_current_memory_usage()
                        if memory and memory > checklist.limit_memory:
                            note = f'exceeded memory limit "{checklist.limit_memory}MB"'
                            errors.append(TaskError(note=note))
                            partial = True
                            break

        # Validate end
        if not partial:
            if not resource.tabular:
                helpers.pass_through(resource.byte_stream)
            for check in connected_checks:
                for error in check.validate_end():
                    if error.code in checklist.scope:
                        errors.append(error)

    # Return report
    return Report.from_task(
        resource,
        errors=errors,
        partial=partial,
        time=timer.time,
        scope=checklist.scope,
    )
