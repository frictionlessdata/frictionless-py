from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .schema import Schema


# TODO: move exception handling to high-level actions?
@Report.from_validate
def validate(schema: "Schema"):
    """Validate schema

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=schema.metadata_errors, tasks=[])
