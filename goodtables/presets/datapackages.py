# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import deepcopy
from .datapackage import datapackage as datapackage_preset
from ..register import preset


# Module API

@preset('datapackages')
def datapackages(items):
    errors = []
    tables = []

    # Add errors, tables
    items = deepcopy(items)
    for item in items:
        source = item.pop('source')
        item_errors, item_tables = datapackage_preset(source, **item)
        errors.extend(item_errors)
        tables.extend(item_tables)

    return errors, tables
