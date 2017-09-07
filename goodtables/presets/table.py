# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from tabulator import Stream
from tableschema import Schema, exceptions
from ..registry import preset


# Module API

@preset('table')
def table(source, schema=None, **options):
    warnings = []
    tables = []

    # Ensure not a datapackage
    if isinstance(source, six.string_types):
        if source.endswith('datapackage.json'):
            warnings.append('Use "datapackage" preset for Data Packages')

    # Prepare schema
    if not warnings:
        if schema is not None:
            try:
                schema = Schema(schema)
            except exceptions.TableSchemaException as error:
                warnings.append(
                    'Table Schema "%s" has a loading error "%s"' %
                    (schema, error))

    # Add table
    if not warnings:
        options.setdefault('headers', 1)
        tables.append({
            'source': str(source) if isinstance(source, six.string_types) else 'inline',
            'stream': Stream(source, **options),
            'schema': schema,
            'extra': {},
        })

    return warnings, tables
