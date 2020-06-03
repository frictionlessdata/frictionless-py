import tabulator
import tableschema
from .. import config
from .. import helpers
from ..row import Row
from ..task import task
from ..errors import Error
from ..headers import Headers
from ..report import Report, ReportTable
from ..checks import BaselineCheck, IntegrityCheck


@task
def validate_table(
    source,
    *,
    # Source
    scheme=None,
    format=None,
    encoding=None,
    compression=None,
    # Headers
    headers_row=1,
    headers_joiner=' ',
    # Fields
    pick_fields=None,
    skip_fields=None,
    limit_fields=None,
    offset_fields=None,
    # Rows
    pick_rows=None,
    skip_rows=None,
    limit_rows=None,
    offset_rows=None,
    # Schema
    schema=None,
    sync_schema=False,
    patch_schema=False,
    infer_type=None,
    infer_names=None,
    infer_sample=100,
    infer_confidence=0.75,
    # Integrity
    lookup=None,
    size=None,
    hash=None,
    # Validation
    pick_errors=None,
    skip_errors=None,
    limit_errors=1000,
    extra_checks=None,
    # Dialect
    **dialect
):
    """Validate table

    # Arguments
        source (any)

        scheme? (str)
        format? (str)
        encoding? (str)
        compression? (str)

        headers_row? (int | int[])
        headers_joiner? (str)

        pick_fields? ((int | str)[])
        skip_fields? ((int | str)[])
        limit_fields? (int)
        offset_fields? (int)

        pick_rows? ((int | str)[])
        skip_rows? ((int | str)[])
        limit_rows? (int)
        offset_rows? (int)

        schema? (str | dict)
        sync_schema? (bool)
        patch_schema? (dict)
        infer_type? (str)
        infer_names? (str[])
        infer_sample? (int)
        infer_confidence? (float)

        lookup? (dict)
        size? (int)
        hash? (str)

        pick_errors? (str[])
        skip_errors? (str[])
        limit_errors? (int)
        extra_checks? (list)

        **dialect (dict)

    # Returns
        Report

    """

    # Prepare state
    fatal = False
    timer = helpers.Timer()
    row_number = 0
    checks = []
    errors = []

    # Prepare errors
    def add_error(error):
        if error.match(pick_errors=pick_errors, skip_errors=skip_errors):
            errors.append(error)

    # Create stream
    stream = tabulator.Stream(
        source,
        scheme=scheme,
        format=format,
        encoding=encoding,
        compression=compression,
        headers=helpers.translate_headers(headers_row),
        multiline_headers_joiner=headers_joiner,
        pick_fields=helpers.translate_pick_fields(pick_fields),
        skip_fields=helpers.translate_skip_fields(skip_fields),
        limit_fields=limit_fields,
        offset_fields=offset_fields,
        pick_rows=helpers.translate_pick_rows(pick_rows),
        skip_rows=helpers.translate_skip_rows(skip_rows),
        limit_rows=limit_rows,
        offset_rows=offset_rows,
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
                infer_headers = infer_names
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

        # Confirm schema
        if schema and len(schema.field_names) != len(set(schema.field_names)):
            message = 'Schemas with duplicate field names are not supported'
            error = tableschema.exceptions.TableSchemaException(message)
            add_error(Error.from_exception(error))
            schema = None
            fatal = True

    # Start checks
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
                fatal = True
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
                for error in check.validate_row(row):
                    add_error(error)

            # Limit errors
            if limit_errors and len(errors) >= limit_errors:
                break

    # Finish checks
    if not fatal:
        for check in checks:
            for error in check.validate_finish():
                add_error(error)

    # Limit errors
    if limit_errors:
        del errors[limit_errors:]

    # Return report
    time = timer.get_time()
    if schema:
        schema = schema.descriptor
    return Report(
        time=time,
        errors=[],
        tables=[
            ReportTable(
                time=time,
                source=str(stream.source),
                scheme=stream.scheme,
                format=stream.format,
                encoding=stream.encoding,
                compression=stream.compression,
                headers=stream.headers,
                headers_row=headers_row,
                headers_joiner=headers_joiner,
                pick_fields=pick_fields,
                skip_fields=skip_fields,
                limit_fields=limit_fields,
                offset_fields=offset_fields,
                pick_rows=pick_rows,
                skip_rows=skip_rows,
                limit_rows=limit_rows,
                offset_rows=offset_rows,
                schema=schema,
                dialect=dialect,
                row_count=row_number,
                errors=errors,
            )
        ],
    )
