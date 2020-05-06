import datetime
from .config import REPORT_PROFILE


class Report(dict):

    # Validation

    def start_validation(self):
        self.__start = datetime.datetime.now()
        self.clear()
        self['time'] = 0
        self['valid'] = True
        self['warnings'] = []
        self['errorCount'] = 0
        self['tableCount'] = 0
        self['tables'] = []

    def add_warning(self, warning):
        self['warnings'].append(warning)

    def add_table(self, table):
        self['tables'].append(table)

    def finish_validation(self):
        self.__finish = datetime.datetime.now()
        self['time'] = (round((self.__finish - self.__start).total_seconds(), 3),)
        self['valid'] = all(table['valid'] for table in self['tables'])
        self['errorCount'] = sum(table['errorCount'] for table in self['tables'])
        self['tableCount'] = len(self['tables'])
        # TODO: validate
        REPORT_PROFILE

    # Exploration

    def flatten(self):
        pass


class ReportTable(dict):

    # Validation

    def start_validation(
        self, *, source, schema, headers, scheme, format, encoding, dialect
    ):
        self.__start = datetime.datetime.now()
        self.clear()
        self['time'] = 0
        self['valid'] = True
        self['source'] = source
        self['schema'] = schema
        self['headers'] = headers
        self['scheme'] = scheme
        self['format'] = format
        self['encoding'] = encoding
        self['dialect'] = dialect
        self['rowCount'] = 0
        self['errorCount'] = 0
        self['errors'] = []

    def add_error(self, error):
        self['errors'].append(error)

    def finish_validation(self, *, row_count):
        self.__finish = datetime.datetime.now()
        self['time'] = (round((self.__finish - self.__start).total_seconds(), 3),)
        self['valid'] = not len(self['errors'])
        self['rowCount'] = row_count
        self['errorCount'] = len(self['errors'])
        # TODO: validate
        REPORT_PROFILE

    # Exploration

    def flatten(self):
        pass
