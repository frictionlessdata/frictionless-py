from .. import helpers
from ..report import Report
from ..errors import TaskError
from ..validate import validate


def validate_dataset(source):
    timer = helpers.Timer()

    try:

        # Validate tasks
        # TODO: rebase on parallel
        reports = []
        for task in source:
            reports.append(validate(**task))

        # Return report
        time = timer.get_time()
        errors = []
        tables = []
        for report in reports:
            errors.extend(report['errors'])
            tables.extend(report['tables'])
        return Report(time=time, errors=errors, tables=tables)

    except Exception as exception:

        # Prepare report
        time = timer.get_time()
        error = TaskError(details=str(exception))

        # Return report
        return Report(time=time, errors=[error], tables=[])
