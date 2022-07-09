from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from ...exception import FrictionlessException
from ...checklist import Checklist
from ...report import Report
from ... import settings
from ... import helpers

if TYPE_CHECKING:
    from ..resource import Resource
    from ...error import Error


def validate(
    self: Resource,
    checklist: Optional[Checklist] = None,
    *,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
    strict: bool = False,
):
    """Validate resource

    Parameters:
        checklist? (checklist): a Checklist object
        strict? (bool): validate metadata as it is

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()
    errors: List[Error] = []
    warnings: List[str] = []
    descriptor = self.to_descriptor()

    # Prepare checklist
    checklist = checklist or self.checklist or Checklist()
    checks = checklist.connect(self)
    if not checklist.metadata_valid:
        errors = checklist.metadata_errors
        return Report.from_validation(time=timer.time, errors=errors)

    # Prepare resource
    try:
        self.open()
    except FrictionlessException as exception:
        self.close()
        errors = [exception.error]
        return Report.from_validation_task(self, time=timer.time, errors=errors)

    # Validate metadata
    metadata = self.from_descriptor(descriptor) if strict else self
    if not metadata.metadata_valid:
        errors = metadata.metadata_errors
        return Report.from_validation_task(self, time=timer.time, errors=errors)

    # Validate data
    with self:

        # Validate start
        for index, check in enumerate(checks):
            for error in check.validate_start():
                if error.code == "check-error":
                    del checks[index]
                if checklist.match(error):
                    errors.append(error)

        # Validate rows
        if self.tabular:
            row_count = 0
            while True:
                row_count += 1

                # Emit row
                try:
                    row = next(self.row_stream)  # type: ignore
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

                # Limit rows
                if limit_rows:
                    if row_count >= limit_rows:
                        warning = f"reached row limit: {limit_rows}"
                        warnings.append(warning)
                        break

                # Limit errors
                if limit_errors:
                    if len(errors) >= limit_errors:
                        errors = errors[:limit_errors]
                        warning = f"reached error limit: {limit_errors}"
                        warnings.append(warning)
                        break

        # Validate end
        if not warnings:
            if not self.tabular:
                helpers.pass_through(self.byte_stream)
            for check in checks:
                for error in check.validate_end():
                    if checklist.match(error):
                        errors.append(error)

    # Return report
    return Report.from_validation_task(
        self,
        time=timer.time,
        scope=checklist.scope,
        errors=errors,
        warnings=warnings,
    )
