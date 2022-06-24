from __future__ import annotations
from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .dialect import Dialect


def validate(dialect: Dialect):
    """Validate dialect

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()
    errors = dialect.metadata_errors
    return Report.from_validation(time=timer.time, errors=errors)
