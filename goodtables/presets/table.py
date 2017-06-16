# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import jsontableschema
from tabulator import Stream
from jsontableschema import Schema, validate
from ..decorators import preset


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
            # TODO: after tableschema-v1 will be ready
            # - we should use Schema(strict=False) to handle schema errors on inspection
            # - it means we don't need to validate schema here, mess with helpers etc
            try:
                from jsontableschema.helpers import load_json_source
                loaded_descriptor = load_json_source(schema)
                validate(loaded_descriptor, no_fail_fast=True)
                schema = Schema(loaded_descriptor)
            except jsontableschema.exceptions.MultipleInvalid as exception:
                for error in exception.errors:
                    warnings.append(
                        'Table schema "%s" has a validation error "%s"' %
                        (schema, str(error).splitlines()[0]))
            except Exception as error:
                warnings.append(
                    'Table Schema "%s" has a loading error "%s"' %
                    (schema, error))

    # Add table
    if not warnings:
        options.setdefault('headers', 1)
        tables.append({
            'source': str(source),
            'stream': Stream(source, **options),
            'schema': schema,
            'extra': {},
        })

    return warnings, tables
