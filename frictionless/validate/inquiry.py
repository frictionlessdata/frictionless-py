from functools import partial
from multiprocessing import Pool
from ..inquiry import Inquiry
from ..report import Report
from ..errors import Error
from .main import validate
from .. import helpers
from .. import exceptions


@Report.from_validate
def validate_inquiry(source):
    """Validate inquiry

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_inquiry`

    Parameters:
        source (dict|str): an inquiry descriptor

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()
    inquiry = Inquiry(source)

    # Create tasks
    tasks = []
    reports = []
    for task in inquiry.tasks:
        source_type = task.get("sourceType") or helpers.detect_source_type(task["source"])
        if source_type == "inquiry":
            error = Error(note="Inquiry cannot contain nested inquiries")
            raise exceptions.FrictionlessException(error)
        if source_type == "package":
            # For now, we don't flatten inquiry completely and for the case
            # of a list of packages with one resource we don't get proper multiprocessing
            report = validate(**helpers.create_options(task))
            reports.append(report)
            continue
        tasks.append(task)

    # Validate task
    if len(tasks) == 1:
        report = validate(**helpers.create_options(tasks[0]))
        reports.append(report)

    # Validate tasks
    if len(tasks) > 1:
        with Pool() as pool:
            reports.extend(pool.map(partial(helpers.apply_function, validate), tasks))

    # Return report
    errors = []
    tables = []
    for report in reports:
        errors.extend(report["errors"])
        tables.extend(report["tables"])
    return Report(time=timer.time, errors=errors, tables=tables)
