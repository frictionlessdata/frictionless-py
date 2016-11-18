# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import jsontableschema
from tabulator import Stream
from jsontableschema import Schema, validate
from ..register import preset
from ..spec import spec


# Module API

@preset('table')
def table(source, schema=None, **options):
    errors = []
    tables = []

    # Prepare schema
    if schema is not None:
        descriptor = schema
        try:
            # https://github.com/frictionlessdata/jsontableschema-py/issues/113
            from jsontableschema.helpers import load_json_source
            loaded_descriptor = load_json_source(schema)
            validate(loaded_descriptor, no_fail_fast=True)
            schema = Schema(loaded_descriptor)
        except jsontableschema.exceptions.MultipleInvalid as exception:
            for error in exception.errors:
                # Error message should contain schema source (often it's path)
                message = spec['errors']['jsontableschema-error']['message']
                message = message.format(
                    error_message='{problem} [{source}]'.format(
                        problem=str(error).splitlines()[0],
                        source=str(descriptor)))
                errors.append({
                    'code': 'jsontableschema-error',
                    'message': message,
                    'row-number': None,
                    'column-number': None,
                })

    # Add table
    if not errors:
        options.setdefault('headers', 1)
        tables.append({
            'source': str(source),
            'stream': Stream(source, **options),
            'schema': schema,
            'extra': {},
        })

    return errors, tables
