from .. import helpers
from ..task import Task
from ..report import Report
from ..validate import validate


@Task.catch
def validate_task(source):
    timer = helpers.Timer()

    # Validate tasks
    # TODO: rebase on parallel
    reports = []
    for options in source:
        reports.append(validate(**options))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
