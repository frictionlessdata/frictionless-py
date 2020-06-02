from .. import helpers
from ..task import task
from ..report import Report
from ..inquiry import Inquiry
from ..validate import validate


@task
def validate_inquiry(source):
    timer = helpers.Timer()
    inquiry = Inquiry(source)

    # Validate tasks
    reports = []
    for inquiry_task in inquiry.tasks:
        reports.append(validate(**inquiry_task))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
