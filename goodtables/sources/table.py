import tabulator
import tableschema
from .. import config
from .. import helpers
from ..row import Row
from ..headers import Headers
from ..errors import Error, TaskError
from ..report import Report, ReportTable
from ..checks import BaselineCheck, IntegrityCheck


# TODO: implement field_limit
# TODO: split on functions?
# TODO: rebase to callable class?
# TODO: use a Task/Validation class inside?
def validate_table(
    source,
    *,
    # Source
    headers=1,
    scheme=None,
    format=None,
    encoding=None,
    compression=None,
    pick_fields=None,
    skip_fields=None,
    field_limit=None,
    pick_rows=None,
    skip_rows=None,
    row_limit=None,
    size=None,
    hash=None,
    # Schema
    schema=None,
    sync_schema=None,
    patch_schema=None,
    infer_type=None,
    infer_sample=100,
    infer_confidence=0.75,
    # Validation
    pick_errors=None,
    skip_errors=None,
    error_limit=1000,
    extra_checks=None,
    # Dialect
    **dialect
):

    # Prepare state
    fatal = False
    timer = helpers.Timer()
    row_number = 0
    checks = []
    errors = []

    try:

        # Prepare errors
        # TODO: rewrite; for now it's a naive algorithm
        def add_error(error):
            if error.match(pick_errors=pick_errors, skip_errors=skip_errors):
                errors.append(error)

        # Create stream
        stream = tabulator.Stream(
            source,
            headers=headers,
            scheme=scheme,
            format=format,
            encoding=encoding,
            compression=compression,
            pick_columns=pick_fields,
            skip_columns=skip_fields,
            pick_rows=pick_rows,
            skip_rows=skip_rows,
            sample_size=infer_sample,
            hashing_algorithm=helpers.parse_hashing_algorithm(hash),
            **dialect
        )

        # Open stream
        try:
            stream.open()
            if not stream.sample:
                message = 'There are no rows available'
                raise tabulator.exceptions.SourceError(message)
        except Exception as exception:
            error = Error.from_exception(exception)
            add_error(error)
            fatal = True

        # Create schema
        try:
            schema = tableschema.Schema(schema or {})
        except tableschema.exceptions.TableSchemaException as exception:
            add_error(Error.from_exception(exception))
            schema = None
            fatal = True

        # Prepare schema
        if not fatal:

            # Infer schema
            if schema and not schema.fields:
                infer_headers = stream.headers
                if not infer_headers:
                    field_numbers = list(range(1, len(stream.sample[0]) + 1))
                    infer_headers = ['field%s' % number for number in field_numbers]
                if infer_type:
                    schema.descriptor['fields'] = []
                    schema.descriptor['missingValues'] = config.MISSING_VALUES
                    for header in infer_headers:
                        field = {'name': header, 'type': infer_type, 'format': 'default'}
                        schema.descriptor['fields'].append(field)
                    schema.commit()
                else:
                    schema.infer(
                        stream.sample, headers=infer_headers, confidence=infer_confidence
                    )

            # Sync schema
            if schema and sync_schema:
                new_fields = []
                old_fields = schema.descriptor.get('fields', [])
                map_fields = {field.get('name'): field for field in old_fields}
                for header in stream.headers:
                    field = map_fields.get(header)
                    if field:
                        new_fields.append(field)
                schema.descriptor['fields'] = new_fields
                schema.commit()

            # Patch schema
            if schema and patch_schema:
                fields = patch_schema.pop('fields', {})
                schema.descriptor.update(patch_schema)
                for field in schema.descriptor['fields']:
                    field.update((fields.get(field.get('name'), {})))
                schema.commit()

            # Validate schema
            if schema and schema.errors:
                for error in schema.errors:
                    add_error(Error.from_exception(error))
                schema = None
                fatal = True

        # Start checks
        # TODO: add support for checks from plugins
        if not fatal:
            Checks = []
            Checks.append(BaselineCheck)
            Checks.append((IntegrityCheck, {'size': size, 'hash': hash}))
            Checks.extend(extra_checks or [])
            for Check in Checks:
                check = Check() if isinstance(Check, type) else Check[0](Check[1])
                checks.append(check)
                for error in check.validate_start(stream=stream, schema=schema):
                    add_error(error)

        # Validate headers
        if not fatal:
            if stream.headers:

                # Get headers
                headers = Headers(
                    stream.headers,
                    fields=schema.fields,
                    field_positions=stream.field_positions,
                )

                # Validate headers
                for check in checks:
                    for error in check.validate_headers(headers):
                        add_error(error)

        # Validate rows
        if not fatal:
            fields = schema.fields
            iterator = stream.iter(extended=True)
            field_positions = stream.field_positions
            if not field_positions:
                field_positions = list(range(1, len(schema.fields) + 1))
            while True:

                # Read cells
                try:
                    row_position, _, cells = next(iterator)
                except StopIteration:
                    break
                except Exception as exception:
                    error = Error.from_exception(exception)
                    add_error(error)
                    stream = None

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
                    for error in check.validate_row(row):
                        add_error(error)

                # Row/error limits
                if row_limit and row_number >= row_limit:
                    break
                if error_limit and len(errors) >= error_limit:
                    break

        # Finish checks
        if not fatal:
            for check in checks:
                for error in check.validate_finish():
                    add_error(error)

        # Return report
        time = timer.get_time()
        if error_limit:
            del errors[error_limit:]
        return Report(
            time=time,
            errors=[],
            tables=[
                ReportTable(
                    time=time,
                    source=str(stream.source),
                    headers=stream.headers,
                    scheme=stream.scheme,
                    format=stream.format,
                    encoding=stream.encoding,
                    compression=stream.compression,
                    schema=schema.descriptor if schema else None,
                    dialect=dialect,
                    row_count=row_number,
                    errors=errors,
                )
            ],
        )

    except Exception as exception:

        # Prepare report
        time = timer.get_time()
        error = TaskError(details=str(exception))

        # Return report
        return Report(time=time, errors=[error], tables=[])
