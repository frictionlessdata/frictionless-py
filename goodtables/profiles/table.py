# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jsontableschema import Table


# Module API

def table(source, **options):
    dataset = []
    # Add table
    dataset.append({
        'table': Table(source, **options),
        'extra': {},
    })
    return dataset
