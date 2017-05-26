# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tabulator import Stream
from jsontableschema import Schema
from jsontableschema.exceptions import SchemaValidationError
from datapackage import DataPackage
from ..decorators import preset


# Module API

@preset('datapackage')
def datapackage(source, **options):
    warnings = []
    tables = []

    # Load datapackage
    try:
        datapackage = DataPackage(source, **options)
    except Exception as error:
        warnings.append(
            'Data Package "%s" has a loading error "%s"' %
            (source, error))

    # Validate datapackage
    if not warnings:
        for error in datapackage.iter_errors():
            warnings.append(
                'Data Package "%s" has a validation error "%s"' %
                (source, str(error).splitlines()[0]))

    # Extract datapackage tables
    if not warnings:
        for resource in datapackage.resources:
            # TODO: after datapackage-v1 will be ready
            # - we should use `resource.tabular` to filter tabular resources
            # - we don't need to validate schema here because of dereferencing
            path = resource.remote_data_path or resource.local_data_path
            try:
                schema = Schema(resource.descriptor['schema'])
            except SchemaValidationError as error:
                warnings.append(
                    'Data Package "%s" has a validation error "%s"' %
                    (source, str(error).splitlines()[0]))
                continue
            except Exception:
                continue
            tables.append({
                'source': path,
                'stream': Stream(path, headers=1),
                'schema': schema,
                'extra': {
                    'datapackage': str(source),
                },
            })

    return warnings, tables
