# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Table, validate
from ..registry import profile


# Module API

@profile('table')
def table(dataset, source, schema=None, **options):
    errors = []

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
                    'message': str(error),
                })

    # Add table
    if not errors:
        dataset.append({
            'table': Table(source, schema, **options),
            'extra': {},
        })

    return errors
