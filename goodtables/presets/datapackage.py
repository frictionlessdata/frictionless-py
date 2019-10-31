# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from tabulator import Stream
from functools import partial
from datapackage import Package, exceptions
from ..registry import preset


# Module API

@preset('datapackage')
def datapackage(source, **options):
    warnings = []
    tables = []

    # Load datapackage
    try:
        package = Package(source, **options)
    except exceptions.DataPackageException as error:
        warnings.append(
            'Data Package "%s" has a loading error "%s"' %
            (source, error))

    # Extract datapackage tables
    if not warnings:
        for resource in package.resources:
            if resource.tabular:
                hash = resource.descriptor.get('hash')
                if hash and not hash.startswith('sha256:'):
                    message = 'Resource "%s" does not use the SHA256 hash. The check will be skipped'
                    warnings.append(message % resource.name)
                tables.append({
                    'source': resource.source if not resource.inline else 'inline',
                    'stream': Stream(partial(_iter_resource_rows, resource), headers=1),
                    'schema': resource.schema,
                    'extra': {
                        'datapackage': json.dumps(source) if isinstance(source, dict) else source,
                        'resource-name': resource.name,
                    },
                })

    # Extrace datapackage errors
    if not warnings:
        for error in package.errors:
            warnings.append(
                'Data Package "%s" has a validation error "%s"' %
                (source, error))

    return warnings, tables


# Internal

def _iter_resource_rows(resource):
    for index, row in enumerate(resource.iter(integrity=True, cast=False)):
        if not index:
            yield resource.headers
        yield row
