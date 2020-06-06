import stringcase
from .. import helpers
from ..report import Report
from ..inquiry import Inquiry
from ..validate import validate


@Report.catch
def validate_inquiry(source):
    timer = helpers.Timer()
    inquiry = Inquiry(source)

    # Validate tasks
    reports = []
    for inquiry_source in inquiry.sources:
        opts = {stringcase.snakecase(key): value for key, value in inquiry_source.items()}
        reports.append(validate(**opts))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
