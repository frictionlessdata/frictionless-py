from functools import partial
from multiprocessing import Pool
from .. import helpers
from .. import exceptions
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

    # Prepare tasks
    tasks = []
    reports = []
    for task in inquiry.tasks:
        source_type = task.get('sourceType') or helpers.detect_source_type(task['source'])
        if source_type == 'inquiry':
            message = 'Inquiry cannot contain nested inquiries'
            raise exceptions.GoodtablesException(message)
        if source_type == 'package':
            # For now, we don't flatten inquiry completely and for the case
            # of a list of packages with one resource we don't get proper multiprocessing
            report = validate(**helpers.create_options_from_descriptor(task))
            reports.append(report)
            continue
        tasks.append(task)

    # Validate task
    if len(tasks) == 1:
        report = validate(**helpers.create_options_from_descriptor(tasks[0]))
        reports.append(report)

    # Validate tasks
    if len(tasks) > 1:
        with Pool() as pool:
            reports.extend(pool.map(partial(helpers.apply_function, validate), tasks))

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
