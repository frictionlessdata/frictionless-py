from .. import helpers
from ..report import Report
from ..schema import Schema
from .. import exceptions


@Report.from_validate
def validate_schema(source):
    """Validate schema

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_schema`

    Parameters:
        source (dict|str): a schema descriptor

    Returns:
        Report: validation report

    """

    # Create state
    timer = helpers.Timer()

    # Create schema
    try:
        schema = Schema(source)
    except exceptions.FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tables=[])

    # Return report
    return Report(time=timer.time, errors=schema.metadata_errors, tables=[])
