import tableschema
from .. import helpers
from ..report import Report
from ..errors import SchemaError


@Report.catch
def validate_schema(source):
    timer = helpers.Timer()

    # Create schema
    try:
        schema = tableschema.Schema(source)
    except tableschema.exceptions.TableSchemaException as exception:
        time = timer.get_time()
        error = SchemaError(details=str(exception))
        return Report(time=time, errors=[error], tables=[])

    # Validate schema
    errors = []
    for error in schema.errors:
        errors.append(SchemaError(details=str(error)))

    # Return report
    time = timer.get_time()
    return Report(time=time, errors=errors, tables=[])
