import functools
from . import config
from . import exceptions
from .helpers import Timer
from .errors import TaskError
from .metadata import Metadata


class Report(Metadata):
    metadata_profile = config.REPORT_PROFILE

    def __init__(self, *, time, errors, tables):
        descriptor = {}
        descriptor['time'] = time
        descriptor['valid'] = not errors and all(tab['valid'] for tab in tables)
        descriptor['version'] = config.VERSION
        descriptor['tableCount'] = len(tables)
        descriptor['errorCount'] = len(errors) + sum(tab['errorCount'] for tab in tables)
        descriptor['errors'] = errors
        descriptor['tables'] = tables
        super().__init__(descriptor)

    @property
    def time(self):
        return self['time']

    @property
    def valid(self):
        return self['valid']

    @property
    def version(self):
        return self['version']

    @property
    def table_count(self):
        return self['tableCount']

    @property
    def error_count(self):
        return self['errorCount']

    @property
    def errors(self):
        return self['errors']

    @property
    def tables(self):
        return self['tables']

    @property
    def table(self):
        if len(self.tables) != 1:
            message = 'The "report.table" is only available for a single table reports'
            raise exceptions.GoodtablesException(message)
        return self.tables[0]

    def flatten(self, spec):
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        for count, table in enumerate(self.tables, start=1):
            for error in table.errors:
                context = {'tableNumber': count, 'tablePosition': count}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result

    # Helpers

    @staticmethod
    def catch(validate):
        @functools.wraps(validate)
        def wrapper(*args, **kwargs):
            timer = Timer()
            try:
                return validate(*args, **kwargs)
            except Exception as exception:
                time = timer.get_time()
                error = TaskError(details=str(exception))
                return Report(time=time, errors=[error], tables=[])

        return wrapper


class ReportTable(Metadata):
    def __init__(
        self,
        *,
        time,
        scope,
        row_count,
        source,
        scheme,
        format,
        encoding,
        compression,
        headers,
        headers_row,
        headers_joiner,
        pick_fields,
        skip_fields,
        limit_fields,
        offset_fields,
        pick_rows,
        skip_rows,
        limit_rows,
        offset_rows,
        schema,
        dialect,
        errors,
    ):
        descriptor = {}
        descriptor['time'] = time
        descriptor['valid'] = not errors
        descriptor['scope'] = scope
        descriptor['rowCount'] = row_count
        descriptor['errorCount'] = len(errors)
        descriptor['source'] = source
        descriptor['scheme'] = scheme
        descriptor['format'] = format
        descriptor['encoding'] = encoding
        descriptor['compression'] = compression
        descriptor['headers'] = headers
        descriptor['headersRow'] = headers_row
        descriptor['headersJoiner'] = headers_joiner
        descriptor['pickFields'] = pick_fields
        descriptor['skipFields'] = skip_fields
        descriptor['limitFields'] = limit_fields
        descriptor['offsetFields'] = offset_fields
        descriptor['pickRows'] = pick_rows
        descriptor['skipRows'] = skip_rows
        descriptor['limitRows'] = limit_rows
        descriptor['offsetRows'] = offset_rows
        descriptor['schema'] = schema
        descriptor['dialect'] = dialect
        descriptor['errors'] = errors
        super().__init__(descriptor)

    @property
    def time(self):
        return self['time']

    @property
    def valid(self):
        return self['valid']

    @property
    def scope(self):
        return self['scope']

    @property
    def row_count(self):
        return self['rowCount']

    @property
    def error_count(self):
        return self['errorCount']

    @property
    def errors(self):
        return self['errors']

    @property
    def error(self):
        if len(self.errors) != 1:
            message = 'The "table.error" is only available for a single error tables'
            raise exceptions.GoodtablesException(message)
        return self.errors[0]

    def flatten(self, spec):
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        return result
