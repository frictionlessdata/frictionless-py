from .. import helpers
from ..exception import FrictionlessException
from ..report import Report
from ..schema import Schema


@Report.from_validate
def validate_schema(source, **options):
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
        native = isinstance(source, Schema)
        schema = source.to_copy() if native else Schema(source, **options)
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Return report
    return Report(time=timer.time, errors=schema.metadata_errors, tasks=[])
