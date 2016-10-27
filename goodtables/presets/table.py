# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import jsontableschema
from jsontableschema import Table, validate
from ..register import preset


# Module API

@preset('table')
def table(source, schema=None, **options):
    errors = []
    tables = []

    # Validate schema
    if schema is not None:
        # https://github.com/frictionlessdata/jsontableschema-py/issues/113
        from jsontableschema.helpers import load_json_source
        schema = load_json_source(schema)
        try:
            validate(schema, no_fail_fast=True)
        except jsontableschema.exceptions.MultipleInvalid as exception:
            for error in exception.errors:
                errors.append({
                    'code': 'jsontableschema-error',
                    'message': str(error).splitlines()[0],
                    'row-number': None,
                    'column-number': None,
                })

    # Add table
    if not errors:
        tables.append({
            'table': Table(source, schema, **options),
            'extra': {},
        })

    return errors, tables
