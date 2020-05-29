from . import config
from . import exceptions
from .metadata import Metadata


class Report(Metadata):
    def __init__(self, *, time, errors, tables):
        descriptor = {}
        descriptor['version'] = config.VERSION
        descriptor['time'] = time
        descriptor['valid'] = not errors and all(tab['valid'] for tab in tables)
        descriptor['errorCount'] = len(errors) + sum(tab['errorCount'] for tab in tables)
        descriptor['tableCount'] = len(tables)
        descriptor['errors'] = errors
        descriptor['tables'] = tables
        # TODO: enable validation
        #  super().__init__(descriptor, strict=True, profile=config.REPORT_PROFILE)
        super().__init__(descriptor, strict=True)

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
        for table_number, table in enumerate(self.tables, start=1):
            for error in table.errors:
                context = {'tableNumber': table_number}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result


class ReportTable(Metadata):
    def __init__(
        self,
        *,
        time,
        source,
        headers,
        scheme,
        format,
        encoding,
        compression,
        schema,
        dialect,
        row_count,
        errors
    ):
        descriptor = {}
        descriptor['time'] = time
        descriptor['valid'] = not errors
        descriptor['source'] = source
        descriptor['headers'] = headers
        descriptor['scheme'] = scheme
        descriptor['format'] = format
        descriptor['encoding'] = encoding
        descriptor['compression'] = compression
        descriptor['schema'] = schema
        descriptor['dialect'] = dialect
        descriptor['rowCount'] = row_count
        descriptor['errorCount'] = len(errors)
        descriptor['errors'] = errors
        super().__init__(descriptor, strict=True)

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
