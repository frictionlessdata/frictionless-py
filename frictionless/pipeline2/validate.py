from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .pipeline import Pipeline


# TODO: move exception handling to high-level actions?
@Report.from_validate
def validate(pipeline: "Pipeline"):
    """Validate pipeline

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=pipeline.metadata_errors, tasks=[])
