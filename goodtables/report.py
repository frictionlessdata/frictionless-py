from .config import REPORT_PROFILE


class Report(dict):
    def __init__(self, *, time, warnings, table_reports):
        pass
        # TODO: validate
        REPORT_PROFILE

    def flatten(self):
        pass


class TableReport(dict):
    def __init__(self, *, time, stream, schema, dialect, row_count, errors):
        self['time'] = time
        self['valid'] = not len(errors)
        self['source'] = stream.source
        self['headers'] = stream.headers
        self['scheme'] = stream.scheme
        self['format'] = stream.format
        self['encoding'] = stream.encoding
        self['compression'] = stream.compression
        self['schema'] = schema.descriptor
        self['dialect'] = dialect
        self['rowCount'] = row_count
        self['errorCount'] = len(errors)
        self['errors'] = errors
        # TODO: validate
        REPORT_PROFILE

    def flatten(self):
        pass
