from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .schema import Schema


def validate(schema: "Schema"):
    """Validate schema

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    errors = schema.metadata_errors
    return Report(errors=errors, time=timer.time)
