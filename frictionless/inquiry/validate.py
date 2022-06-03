from typing import TYPE_CHECKING
from ..report import Report

if TYPE_CHECKING:
    from .inquiry import Inquiry


# TODO: make only metadata validation -- data validation in resource/package.validate
# TODO: move run here?
# TODO: move exception handling to other layer?
@Report.from_validate
def validate(inquiry: "Inquiry", *, parallel=False):
    """Validate inquiry

    Parameters:
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """
    return inquiry.run(parallel=parallel)
