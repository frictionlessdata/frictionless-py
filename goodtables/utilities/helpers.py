# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import inspect
import requests
from .. import compat
from .. import exceptions


def builtin_processors():
    """Return dict of public builtin processors. Avoids circular import."""
    from .. import processors
    return {
        processors.StructureProcessor.name: processors.StructureProcessor,
        processors.SchemaProcessor.name: processors.SchemaProcessor
    }


DEFAULT_PIPELINE = ('structure',)
REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')


# a schema for the reporter.Report() instances used by validators
report_schema = {
    'processor': {'type': compat.str},
    'result_category': {'type': compat.str},
    'result_level': {'type': compat.str},
    'result_message': {'type': compat.str},
    'result_id': {'type': compat.str},
    'result_name': {'type': compat.str},
    'result_context': {'type': list},
    'row_index': {'type': (int, type(None))},
    'row_name': {'type': compat.str},
    'column_index': {'type': (int, type(None))},
    'column_name': {'type': compat.str}
}


def get_report_result_types():
    """Return a list of all builtin result types."""

    result_types = []

    for processor in builtin_processors().values():
        result_types.extend([r[1] for r in
                             tuple(processor.RESULT_TYPES.items())])

    return result_types


def pipeline_stats(report):
    """Generates high-level pipeline statistics from a report."""

    def _bad_type_percent(column_name, results, row_count):
        """Return a percentage for amount of data with bad type in a column."""

        match_count = len([r for r in results if
                           r['result_id'] == 'schema_003' and
                           r['column_name'] == column_name])

        return int((match_count/row_count) * 100)

    bad_row_count = len(set([r['row_index'] for r in report['results'] if
                             r['result_category'] == 'row' and
                             r['result_level'] == 'error' and
                             r['row_index'] is not None]))

    bad_column_count = len(set([r['column_index'] for r in report['results'] if
                                r['result_category'] == 'row' and
                                r['result_level'] == 'error' and
                                r['column_index'] is not None]))

    columns = [{'name': header, 'index': index,
                'bad_type_percent': _bad_type_percent(header, report['results'],
                                                      report['meta']['row_count'])}
               for index, header in enumerate(report['meta']['headers'])]

    report['meta'].update({
        'bad_row_count': bad_row_count,
        'bad_column_count': bad_column_count,
        'columns': columns
    })

    return report


def load_json_source(source):

    """Load a JSON source, from string, URL or buffer,  into a Python type."""

    if source is None:
        return None

    elif isinstance(source, (dict, list)):
        # the source has already been loaded
        return source

    elif compat.parse.urlparse(source).scheme in REMOTE_SCHEMES:
        return json.loads(requests.get(source).text)

    elif isinstance(source, compat.str) and not os.path.exists(source):
        return json.loads(source)

    else:
        with io.open(source, encoding='utf-8') as stream:
            source = json.load(io.open(source, encoding='utf-8'))
        return source


def validate_handler(handler, argcount=1):

    """Validate a handler.

    Args:
        * `handler`: the supposed handler, which is a function
        * `argcount`: the count of args the handler should take
        (not including self if handler is a method)
    """

    if handler is None:
        return True
    else:
        if not callable(handler):
            raise exceptions.InvalidHandlerError

        if inspect.ismethod(handler):
            # extra arg for self
            argcount += 1

        spec = inspect.getargspec(handler)
        if not len(spec[0]) == argcount:
            raise exceptions.InvalidHandlerError
