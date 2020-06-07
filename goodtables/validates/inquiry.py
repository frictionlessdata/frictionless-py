from functools import partial
from multiprocessing import Pool
from .. import helpers
from ..report import Report
from ..inquiry import Inquiry
from ..validate import validate


@Report.catch
def validate_inquiry(source):
    timer = helpers.Timer()
    inquiry = Inquiry(source)

    # Validate tasks
    with Pool() as pool:
        reports = pool.map(
            partial(helpers.apply_function, validate),
            (descriptor for descriptor in inquiry.tasks),
        )

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
