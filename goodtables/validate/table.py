import tabulator
import tableschema
from ..row import Row
from ..error import Error
from ..timer import Timer
from ..headers import Headers
from ..report import TableReport
from ..checks import BaselineCheck


def validate_table(
    source,
    *,
    # Source
    headers=None,
    scheme=None,
    format=None,
    encoding=None,
    compression=None,
    pick_rows=None,
    skip_rows=None,
    pick_fields=None,
    skip_fields=None,
    dialect=None,
    schema=None,
    order_schema=None,
    # Validation
    pick_errors=None,
    skip_errors=None,
    row_limit=None,
    error_limit=None,
    extra_checks=None,
    **task_rest
):

    # Prepare state
    timer = Timer()
    checks = []
    errors = []

    # Prepare stream
    try:
        stream = tabulator.Stream(
            source,
            headers=headers or 1,
            scheme=scheme,
            format=format,
            encoding=encoding,
            compression=compression,
            pick_rows=pick_rows,
            skip_rows=skip_rows,
            pick_columns=pick_fields,
            skip_columns=skip_fields,
            **dialect,
            **task_rest
        )
        stream.open()
    except Exception as exception:
        error = Error.from_exception(exception)
        errors.append(error)
        stream = None

    # Prepare schema
    if stream:
        if not schema:
            schema = tableschema.Schema()
            schema.infer(stream.sample, headers=stream.headers, confidence=1)
        if order_schema:
            # TODO: implement order_schema
            pass

    # Prepare checks
    if stream and schema:
        checks = [BaselineCheck(stream=stream, schema=schema)]
        # for plugin in plugins:
        #   check = plugin.create_check(stream=stream, schema=schema)
        #   checks.append(check)
        pass

    # Validate headers
    if stream and schema:

        # Get headers
        headers = Headers(
            stream.headers, fields=schema.fields, field_positions=schema.field_positions
        )

        # Validate headers
        for check in checks:
            # TODO: filter pick/skip errors
            errors.extend(check.validate_table_headers(headers))

    # Validate rows
    row_number = 0
    fields = schema.fields
    field_positions = stream.field_positions
    iterator = stream.iter(extended=True)
    while True:

        # Read cells
        try:
            row_position, _, cells = next(iterator)
        except Exception as exception:
            error = Error.from_exception(exception)
            errors.append(error)
            stream = None
        except StopIteration:
            break

        # Create row
        row_number += 1
        row = Row(
            cells,
            fields=fields,
            field_positions=field_positions,
            row_position=row_position,
            row_number=row_number,
        )

        # Validate row
        for check in checks:
            # TODO: filter pick/skip errors
            errors.extend(check.validate_table_row(row))

        # TODO: handle row/error limits

    # Return report
    return TableReport(
        time=timer.get_time(),
        stream=stream,
        schema=schema,
        dialect={},
        row_count=row_number,
        errors=errors,
    )
