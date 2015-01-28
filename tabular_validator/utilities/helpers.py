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


def builtin_validators():
    """Return dict of public builtin validators. Avoids circular import."""
    from .. import validators
    return {
        validators.StructureValidator.name: validators.StructureValidator,
        validators.TableSchemaValidator.name: validators.TableSchemaValidator
    }


DEFAULT_PIPELINE = ('structure',)
REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')


# a schema for the reporter.Report() instances used by validators
report_schema = {
    'name': {'type': compat.str},
    'category': {'type': compat.str},
    'level': {'type': compat.str},
    'position': {'type': (int, type(None))},
    'message': {'type': compat.str}
}


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
