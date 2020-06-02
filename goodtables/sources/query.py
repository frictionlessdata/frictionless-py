from .. import helpers
from ..task import task
from ..report import Report
from ..validate import validate


@task
def validate_query(source):
    timer = helpers.Timer()

    # Validate tasks
    # TODO: rebase on parallel
    reports = []
    for options in source.get('tasks', []):
        reports.append(validate(**options))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
