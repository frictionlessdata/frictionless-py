# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Table
from datapackage import DataPackage


# Module API

def datapackage(source, **options):
    dataset = []
    datapackage = DataPackage(source, **options)
    datapackage.validate()
    for resource in datapackage.resources:
        path = resource.remote_data_path or resource.local_data_path
        table = Table(path, schema=resource.descriptor['schema'])
        extra = {
            'datapackage': datapackage.descriptor.get('name'),
            'resource': resource.descriptor.get('name'),
        }
        # Add table
        dataset.append({
            'table': table,
            'extra': extra,
        })
    return dataset
