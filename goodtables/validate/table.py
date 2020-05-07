import datetime
import tabulator
import tableschema
from ..row import Row
from ..spec import Spec
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
    pick_lines=None,
    skip_lines=None,
    pick_columns=None,
    skip_columns=None,
    dialect=None,
    schema=None,
    order_schema=None,
    # Validation
    pick_errors=None,
    skip_errors=None,
    row_limit=None,
    error_limit=None,
    extra_checks=None,
    spec=None,
    **task_rest
):

    # Prepare state
    spec = spec or Spec()
    timer = datetime.datetime.now()
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
            pick_rows=pick_lines,
            skip_rows=skip_lines,
            pick_columns=pick_columns,
            skip_columns=skip_columns,
            **dialect,
            **task_rest
        )
        stream.open()
    except Exception as exception:
        error = spec.create_error_from_exception(exception)
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
        checks = [BaselineCheck(spec, stream=stream, schema=schema)]
        # for plugin in plugins:
        #   check = plugin.create_check(spec, stream=stream, schema=schema)
        #   checks.append(check)
        pass

    # Validate headers
    if stream and schema:
        for check in checks:
            errors.extend(check.validate_table_headers(stream.headers))

    # Validate rows
    row_number = 0
    iterator = stream.iter(extended=True)
    while True:
        try:
            line_number, headers, cells = next(iterator)
            row_number += 1
            row = Row(
                cells,
                field_names=schema.field_names,
                line_number=line_number,
                row_number=row_number,
            )
        except Exception as exception:
            error = spec.create_error_from_exception(exception)
            errors.append(error)
            stream = None
        except StopIteration:
            break
        for check in checks:
            errors.extend(check.validate_table_row(row))
        # TODO: handle row/error limits

    # Compose table report
    table_report = TableReport()

    return table_report
