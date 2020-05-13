from .config import REPORT_PROFILE
from . import exceptions


class Report(dict):
    """
    # Arguments
        time (str)
        warnings (str[])
        tables (TableReport[])
    """

    def __init__(self, **context):
        self.update(context)
        self['valid'] = all(table['valid'] for table in context['tables'])
        self['errorCount'] = sum(table['errorCount'] for table in context['tables'])
        self['tableCount'] = len(context['tables'])
        # TODO: validate
        REPORT_PROFILE

    @property
    def table(self):
        if len(self['tables'] != 1):
            message = 'The "report.table" is only available for a single table reports'
            raise exceptions.GoodtablesException(message)
        return self['tables'][0]

    def flatten(self, spec):
        result = []
        for table_number, table in enumerate(self['tables'], start=1):
            for error in table['errors']:
                context = {'tableNumber': table_number}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result


class ReportTable(dict):
    """
    # Arguments
        time (str)
        warnings (str[])
        source (str)
        headers (str[])
        scheme (str)
        format (str)
        encoding (str)
        schema (dict)
        dialect (dict)
        row_count (int)
        errors (Error[])
    """

    def __init__(self, **context):
        self.update(context)
        self['valid'] = not context['errors']
        self['errorCount'] = len(context['errors'])

    @property
    def error(self):
        if len(self['errors'] != 1):
            message = 'The "report_table.error" is only available if one error'
            raise exceptions.GoodtablesException(message)
        return self['errors'][0]

    def flatten(self, spec):
        result = []
        for error in self['errors']:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        return result
