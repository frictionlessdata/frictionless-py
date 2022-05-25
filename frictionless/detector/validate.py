from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .detector import Detector


# TODO: move exception handling to high-level actions?
@Report.from_validate
def validate(detector: "Detector"):
    """Validate detector

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=detector.metadata_errors, tasks=[])
