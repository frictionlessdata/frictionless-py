from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from ...exception import FrictionlessException
from ...checklist import Checklist
from ...report import Report
from ... import settings
from ... import helpers

if TYPE_CHECKING:
    from ...interfaces import ICallbackFunction
    from ..resource import Resource
    from ...error import Error


def validate(
    self: Resource,
    checklist: Optional[Checklist] = None,
    *,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
    on_row: Optional[ICallbackFunction] = None,
):
    """Validate resource

    Parameters:
        checklist? (checklist): a Checklist object

    Returns:
        Report: validation report

    """

    # Create state
    partial = False
    timer = helpers.Timer()
    labels: List[str] = []
    errors: List[Error] = []
    warnings: List[str] = []

    # Prepare checklist
    checklist = checklist or self.checklist or Checklist()
    checks = checklist.connect(self)

    # Validate metadata
    try:
        self.to_descriptor()
    except FrictionlessException as exception:
        return Report.from_validation_task(
            self, time=timer.time, errors=exception.to_errors()
        )

    # Ignore not-supported hashings
    if self.custom.get("hash"):
        warning = "hash is ignored; supported algorithms: md5/sha256"
        warnings.append(warning)

    # Prepare resource
    if self.closed:
        try:
            self.open()
        except FrictionlessException as exception:
            self.close()
            return Report.from_validation_task(
                self, time=timer.time, errors=exception.to_errors()
            )

    # Validate data
    with self:

        # Validate start
        for index, check in enumerate(checks):
            for error in check.validate_start():
                if error.type == "check-error":
                    del checks[index]
                if checklist.match(error):
                    errors.append(error)

        # Validate file
        if not self.tabular:
            helpers.pass_through(self.byte_stream)

        # Validate table
        if self.tabular:
            row_count = 0
            labels = self.labels
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
        self, time=timer.time, labels=labels, errors=errors, warnings=warnings
    )
