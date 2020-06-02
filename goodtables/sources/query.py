from .. import helpers
from ..task import task
from ..query import Query
from ..report import Report
from ..validate import validate


@task
def validate_query(source):
    timer = helpers.Timer()
    query = Query(source)

    # Validate tasks
    reports = []
    for query_task in query.tasks:
        reports.append(validate(**query_task))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
