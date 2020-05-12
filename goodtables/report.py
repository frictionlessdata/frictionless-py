from .config import REPORT_PROFILE


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

    def flatten(self, spec):
        result = []
        for table_number, table in enumerate(self['tables'], start=1):
            for error in table['errors']:
                context = {'tableNumber': table_number}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result


class TableReport(dict):
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
        # TODO: validate
        REPORT_PROFILE

    def flatten(self, spec):
        result = []
        for error in self['errors']:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        return result
