# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import deepcopy
from ..decorators import preset
from .. import exceptions


# Module API

@preset('nested')
def nested(source, presets):
    warnings = []
    tables = []

    # Add warnings, tables
    source = deepcopy(source)
    for item in source:
        preset = item.pop('preset', 'table')
        if preset == 'nested':
            message = 'Preset "nested" supports only one level depth'
            raise exceptions.GoodtablesException(message)
        try:
            preset_func = presets[preset]
        except KeyError:
            message = 'Preset "%s" is not registered' % preset
            raise exceptions.GoodtablesException(message)
        item_warnings, item_tables = preset_func(**item)
        warnings.extend(item_warnings)
        tables.extend(item_tables)

    return warnings, tables
