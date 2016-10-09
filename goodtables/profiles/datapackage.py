# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Table
from datapackage import DataPackage
from ..registry import profile


# Module API

@profile('datapackage')
def datapackage(dataset, source, **options):
    errors = []

    # Validate datapackage
    datapackage = DataPackage(source, **options)
    for exception in datapackage.iter_errors():
        errors.append({
            'code': 'datapackage-error',
            'message': str(exception),
        })

    # Add tables
    if not errors:
        for resource in datapackage.resources:
            path = resource.remote_data_path or resource.local_data_path
            table = Table(path, schema=resource.descriptor['schema'])
            extra = {
                'datapackage': datapackage.descriptor.get('name'),
                'resource': resource.descriptor.get('name'),
            }
            dataset.append({
                'table': table,
                'extra': extra,
            })

    return errors
