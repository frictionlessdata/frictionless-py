# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from .inspector import Inspector


# Module API

def validate(source, **options):
    """https://github.com/frictionlessdata/goodtables-py#validate
    """

    # Extract settings
    validation_options = set((
        'checks',
        'skip_checks',
        'infer_schema',
        'infer_fields',
        'order_fields',
        'error_limit',
        'table_limit',
        'row_limit',
        'custom_presets',
        'custom_checks',
    ))
    settings = dict((
        (key, options.pop(key)) for key in validation_options
        if key in options
    ))

    # Support for pathlib.Path
    if hasattr(source, 'joinpath'):
        source = str(source)
    if isinstance(source, list):
        if source and isinstance(source[0], dict) and 'source' in source[0]:
            for index, item in enumerate(source):
                if hasattr(item['source'], 'joinpath'):
                    source[index]['source'] = str(item['source'])

    # Extract/infer preset
    preset = options.pop('preset', None)
    if preset is None:
        preset = 'table'
        if isinstance(source, six.string_types):
            if source.endswith('datapackage.json'):
                preset = 'datapackage'
        elif isinstance(source, dict):
            if 'resources' in source:
                preset = 'datapackage'
        elif isinstance(source, list):
            if source and isinstance(source[0], dict) and 'source' in source[0]:
                preset = 'nested'

    # Validate
    inspector = Inspector(**settings)
    report = inspector.inspect(source, preset=preset, **options)

    return report
