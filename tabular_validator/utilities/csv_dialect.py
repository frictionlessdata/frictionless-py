# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import jsonschema
from . import helpers


def validate(source):
    """Validate a CSV Dialect source file."""

    schemafile = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'schemas',
        'csv-dialect-description-format.json'))

    with io.open(schemafile) as stream:
        schema = json.load(stream)

    try:
        source = helpers.load_json_source(source)
        jsonschema.validate(source, schema)
        return True

    except (jsonschema.ValidationError, ValueError, TypeError):
        return False
