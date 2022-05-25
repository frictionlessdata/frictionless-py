from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .status import Status


# TODO: move exception handling to high-level actions?
@Report.from_validate
def validate(status: "Status"):
    """Validate status

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=status.metadata_errors, tasks=[])
