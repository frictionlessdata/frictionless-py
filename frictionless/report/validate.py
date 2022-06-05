from typing import TYPE_CHECKING
from .. import helpers

if TYPE_CHECKING:
    from .report import Report


def validate(report: "Report"):
    """Validate report

    Returns:
        Report: validation report
    """
    Report = type(report)
    timer = helpers.Timer()
    errors = report.metadata_errors
    return Report(errors=errors, time=timer.time)
