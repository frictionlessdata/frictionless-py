from ..inquiry import Inquiry
from ..report import Report


@Report.from_validate
def validate_inquiry(source, *, parallel=False, **options):
    """Validate inquiry

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_inquiry`

    Parameters:
        source (dict|str): an inquiry descriptor
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """
    native = isinstance(source, Inquiry)
    inquiry = source.to_copy() if native else Inquiry(source, **options)
    return inquiry.run(parallel=parallel)
