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


def basic_report(report):
    """Run meta statistics."""

    report = set_meta_stats(report)

    return report


def grouped_report(report):
    """Run meta statistics and group the results by row."""

    report = set_meta_stats(report)
    report = group_results(report)

    return report


def set_meta_stats(report):

    """Set run statistics on the report meta object."""

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


def group_results(report):

    """Group report results by row."""

    # If the report is a base error
    base_reports = [result for result in report['results']
                    if result['processor'] == 'base']
    if any(base_reports):
        group_report = {'':{'result_context': [], 'results': base_reports }}
        report['results']= [ group_report ]
        return report

    _rows = set([r['row_index'] for r in report['results']
                 if r['row_index'] is not None])

    def make_groups(results, rows):
        groups = {}

        for row in rows:
            groups.update({
                row: {
                    'row_index': row,
                    'results': []
                }
            })

        for index, result in enumerate(results):
            if result['row_index'] is not None:

                # set the result context on the group
                if not groups[result['row_index']].get('result_context'):
                    groups[result['row_index']]['result_context'] = result['result_context']

                groups[result['row_index']]['results'].append(result)

                # remove stuff we do not require per result
                del result['result_context']
                del result['row_index']

        return groups

    report['results'] = sorted([{k: v} for k, v in make_groups(report['results'], _rows).items()],
                               key=lambda result: list(result.keys())[0])
    return report


def load_json_source(source):

    """Load a JSON source, from string, URL or buffer,  into a Python type."""

    if source is None:
        return None

    elif isinstance(source, (dict, list)):
        # the source has already been loaded
        return source

    elif compat.urlparse(source).scheme in REMOTE_SCHEMES:
        valid_url = make_valid_url(source)
        return json.loads(requests.get(valid_url).text)

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

def make_valid_url(url):
    """Make sure url doesn't contain unsupported characters

    Args:
        * `url`: a url string
    """
    if '/+/http' in url:
        glue = '/+/'
        quoted = [make_valid_url(unquoted) for unquoted in url.split(glue)]
        return (glue).join(quoted)

    scheme, netloc, path, query, fragment = compat.urlsplit(url)
    quoted_path = compat.quote(path.encode('utf-8'))
    quoted_query = compat.quote_plus(query.encode('utf-8'))
    new_url_tuple = (scheme, netloc, quoted_path, quoted_query, fragment)
    quoted_url = compat.urlunsplit(new_url_tuple)
    return quoted_url
