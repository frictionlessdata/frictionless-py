from functools import partial
from multiprocessing import Pool
from ..exception import FrictionlessException
from ..inquiry import Inquiry
from ..system import system
from ..report import Report
from ..errors import Error
from .main import validate
from .. import helpers


@Report.from_validate
def validate_inquiry(source, *, nopool=False, **options):
    """Validate inquiry

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_inquiry`

    Parameters:
        source (dict|str): an inquiry descriptor
        nopool? (bool): disable multiprocessing

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()
    native = isinstance(source, Inquiry)
    inquiry = source.to_copy() if native else Inquiry(source, **options)

    # Create tasks
    tasks = []
    reports = []
    for task in inquiry.tasks:
        type = task.get("type", system.create_file(task["source"]).type)
        if type == "inquiry":
            error = Error(note="Inquiry cannot contain nested inquiries")
            raise FrictionlessException(error)
        if type == "package":
            # TODO:
            # For now, we don't flatten inquiry completely and for the case
            # of a list of packages with one resource we don't get proper multiprocessing
            report = validate(**helpers.create_options(task))
            reports.append(report)
            continue
        tasks.append(task)

    # Validate sequentially
    if len(tasks) == 1 or nopool:
        for task in tasks:
            report = validate(**helpers.create_options(task))
            reports.append(report)

    # Validate in-parallel
    else:
        with Pool() as pool:
            reports.extend(pool.map(partial(helpers.apply_function, validate), tasks))

    # Return report
    errors = []
    tasks = []
    for report in reports:
        errors.extend(report["errors"])
        tasks.extend(report["tasks"])
    return Report(time=timer.time, errors=errors, tasks=tasks)
