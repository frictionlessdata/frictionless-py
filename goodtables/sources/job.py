from .. import helpers
from ..job import Job
from ..task import task
from ..report import Report
from ..validate import validate


@task
def validate_job(source):
    timer = helpers.Timer()
    job = Job(source)

    # Validate tasks
    reports = []
    for job_task in job.tasks:
        reports.append(validate(**job_task))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
