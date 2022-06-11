from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .inquiry import Inquiry


# TODO: return data validation
def validate(inquiry: "Inquiry", *, parallel=False):
    """Validate inquiry

    Parameters:
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """
    timer = helpers.Timer()
    errors = inquiry.metadata_errors
    return Report.from_validation(time=timer.time, errors=errors)
