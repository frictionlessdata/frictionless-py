# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tabulator import Stream
from jsontableschema import Schema
from datapackage import DataPackage
from ..register import preset


# Module API

@preset('datapackage')
def datapackage(source, **options):
    errors = []
    tables = []

    # Prepare datapackage
    datapackage = DataPackage(source, **options)
    for exception in datapackage.iter_errors():
        errors.append({
            'code': 'datapackage-error',
            'message': str(exception).splitlines()[0],
            'row-number': None,
            'column-number': None,
        })

    # Add tables
    if not errors:
        for resource in datapackage.resources:
            path = resource.remote_data_path or resource.local_data_path
            tables.append({
                'stream': Stream(path, headers=1),
                'schema': Schema(resource.descriptor['schema']),
                'extra': {
                    'datapackage': datapackage.descriptor.get('name'),
                    'resource': resource.descriptor.get('name'),
                },
            })

    return errors, tables
