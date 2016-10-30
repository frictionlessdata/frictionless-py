# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import jsontableschema
from tabulator import Stream
from jsontableschema import Schema, validate
from .table import table as table_preset
from ..register import preset


# Module API

@preset('tables')
def tables(items):
    errors = []
    tables = []

    # Add errors, tables
    for item in items:
        source = item.pop('source')
        item_errors, item_tables = table_preset(source, **item)
        errors.extend(item_errors)
        tables.extend(item_tables)

    return errors, tables
