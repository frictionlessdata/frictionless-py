from typing import TYPE_CHECKING
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .inquiry import Inquiry


@Report.from_validate
def validate(inquiry: "Inquiry", *, parallel=False):
    """Validate inquiry

    Parameters:
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """
    timer = helpers.Timer()
    return Report(time=timer.time, errors=inquiry.metadata_errors, tasks=[])
