from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .detector import Detector


def validate(detector: "Detector"):
    """Validate detector

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    # TODO: enable when Detector is Metadata
    errors = detector.metadata_errors  # type: ignore
    return Report(errors=errors, time=timer.time)
