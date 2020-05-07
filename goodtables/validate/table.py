import datetime
import tabulator
import tableschema
from ..spec import Spec


def validate_table(
    source,
    *,
    # Source
    schema=None,
    headers=None,
    scheme=None,
    format=None,
    encoding=None,
    dialect=None,
    # Validation
    spec=None,
    order_fields=None,
    skip_errors=None,
    pick_errors=None,
    row_limit=None,
    error_limit=None,
    **task_rest
):

    # Initialize
    time_start = datetime.datetime.now()
    is_fatal_error = False
    spec = spec or Spec()
    row_count = 0
    errors = []

    # Prepare table
    try:
        stream = tabulator.Stream(
            source,
            headers=headers,
            scheme=scheme,
            format=format,
            encoding=encoding,
            **task_rest
        )
        stream.open()
        sample = stream.sample
        headers = stream.headers
        if headers is None:
            headers = [None] * len(sample[0]) if sample else []
    except Exception as exception:
        error = _compose_error_from_exception(exception)
        errors.append(error)
        is_fatal_error = True


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
