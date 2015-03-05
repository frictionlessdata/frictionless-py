# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import requests
from .. import compat


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
