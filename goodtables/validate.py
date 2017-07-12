# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from .inspector import Inspector


# Module API

def validate(source, **options):
    """https://github.com/frictionlessdata/goodtables-py#validate
    """

    # Extract settings
    settings = {}
    settings['checks'] = options.pop('checks', None)
    settings['infer_schema'] = options.pop('infer_schema', None)
    settings['infer_fields'] = options.pop('infer_fields', None)
    settings['order_fields'] = options.pop('order_fields', None)
    settings['error_limit'] = options.pop('error_limit', None)
    settings['table_limit'] = options.pop('table_limit', None)
    settings['row_limit'] = options.pop('row_limit', None)
    settings['custom_presets'] = options.pop('custom_presets', None)
    settings['custom_checks'] = options.pop('custom_checks', None)
    settings = {key: value for key, value in settings.items() if value is not None}

    # Validate
    inspector = Inspector(**settings)
    report = inspector.inspect(source, **options)

    return report
