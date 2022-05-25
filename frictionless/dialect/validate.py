from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .dialect import Dialect


# TODO: move exception handling to high-level actions?
@Report.from_validate
def validate(dialect: "Dialect"):
    """Validate dialect

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=dialect.metadata_errors, tasks=[])
