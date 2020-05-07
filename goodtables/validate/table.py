import datetime
import tabulator
import tableschema
from . import helpers
from ..spec import Spec
from ..report import TableReport


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
    spec=None,
    **task_rest
):

    # Prepare state
    spec = spec or Spec()
    timer = datetime.datetime.now()
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

    # Validate headers
    if stream and schema:
        errors.extend(validate_table_headers(spec, stream=stream, schema=schema))
        # TODO: include plugins

    # Validate rows

    # Compose report


# Internal


def validate_table_headers(spec, *, stream, schema):
    errors = []

    # Iterate headers
    missing = helpers.combine.missing
    iterator = helpers.combine(schema.field_names, stream.headers)
    for field_number, [field_name, header] in enumerate(iterator, start=1):

        # blank-header
        if header in (None, ''):
            errors.append(
                spec.create_error(
                    'blank-header',
                    context={'headers': stream.headers, 'fieldNumber': field_number},
                )
            )

        # duplicated-header
        prev_headers = stream.headers[0 : field_number - 1]
        duplicate_field_numbers = helpers.find_positions(prev_headers, header)
        if duplicate_field_numbers:
            errors.append(
                spec.create_error(
                    'duplicate-header',
                    context={
                        'header': header,
                        'headers': stream.headers,
                        'fieldNumber': field_number,
                        'details': ', '.join(duplicate_field_numbers),
                    },
                )
            )

        # extra-header
        if field_name == missing:
            errors.append(
                spec.create_error(
                    'extra-header',
                    context={
                        'header': header,
                        'headers': stream.headers,
                        'fieldNumber': field_number,
                    },
                )
            )

        # missing-header
        if header == missing:
            errors.append(
                spec.create_error(
                    'missing-header',
                    context={
                        'headers': stream.headers,
                        'fieldName': field_name,
                        'fieldNumber': field_number,
                    },
                )
            )

        # non-matching-header
        if missing not in [field_name, header] and field_name != header:
            errors.append(
                spec.create_error(
                    'non-matching-header',
                    context={
                        'header': header,
                        'headers': stream.headers,
                        'fieldName': field_name,
                        'fieldNumber': field_number,
                    },
                )
            )

    return errors
