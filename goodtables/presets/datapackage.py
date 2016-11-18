# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tabulator import Stream
from jsontableschema import Schema
from datapackage import DataPackage
from ..register import preset
from ..spec import spec


# Module API

@preset('datapackage')
def datapackage(source, **options):
    errors = []
    tables = []

    # Prepare datapackage
    datapackage = DataPackage(source, **options)
    for exception in datapackage.iter_errors():
        # Error message should contain datapackage source (often it's path)
        message = spec['errors']['datapackage-error']['message']
        message = message.format(
            error_message='{problem} [{source}]'.format(
                problem=str(exception).splitlines()[0],
                source=str(source)))
        errors.append({
            'code': 'datapackage-error',
            'message': message,
            'row-number': None,
            'column-number': None,
        })

    # Add tables
    if not errors:
        for resource in datapackage.resources:
            path = resource.remote_data_path or resource.local_data_path
            tables.append({
                'source': path,
                'stream': Stream(path, headers=1),
                'schema': Schema(resource.descriptor['schema']),
                'extra': {
                    'datapackage': str(source),
                },
            })

    return errors, tables
