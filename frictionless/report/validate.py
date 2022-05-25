from typing import TYPE_CHECKING
from .. import helpers

if TYPE_CHECKING:
    from .report import Report


def validate(report: "Report"):
    """Validate report

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    Report = type(report)
    return Report(time=timer.time, errors=report.metadata_errors, tasks=[])
