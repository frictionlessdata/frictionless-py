from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .pipeline import Pipeline


def validate(pipeline: "Pipeline"):
    """Validate pipeline

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    errors = pipeline.metadata_errors
    return Report.from_validation(time=timer.time, errors=errors)
