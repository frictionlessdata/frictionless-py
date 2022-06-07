from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .status import Status


def validate(status: "Status"):
    """Validate status

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    errors = status.metadata_errors
    return Report(errors=errors, time=timer.time)
