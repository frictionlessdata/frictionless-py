import datetime
import tabulator
import tableschema
from ..spec import Spec


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
    # Validation
    order_fields=None,
    pick_errors=None,
    skip_errors=None,
    row_limit=None,
    error_limit=None,
    extra_checks=None,
    spec=None,
    **task_rest
):

    # Prepare state
    time_start = datetime.datetime.now()
    spec = spec or Spec()
    row_count = 0
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
        error = _compose_error_from_exception(exception)
        errors.append(error)
        stream = None

    # Prepare schema
    if stream:
        if not schema:
            schema = tableschema.Schema()
            schema.infer(stream.sample, headers=stream.headers, confidence=1)
        if order_fields:
            # TODO: implement order_fields
            pass


# Internal


def _compose_error_from_exception(spec, exception):
    code = 'source-error'
    details = str(exception)

    if isinstance(exception, tabulator.exceptions.SourceError):
        code = 'source-error'
    elif isinstance(exception, tabulator.exceptions.SchemeError):
        code = 'scheme-error'
    elif isinstance(exception, tabulator.exceptions.FormatError):
        code = 'format-error'
    elif isinstance(exception, tabulator.exceptions.EncodingError):
        code = 'encoding-error'
    elif isinstance(exception, tabulator.exceptions.IOError):
        code = 'io-error'
    elif isinstance(exception, tabulator.exceptions.HTTPError):
        code = 'http-error'

    return spec.create_error(code, context={'details': details})
