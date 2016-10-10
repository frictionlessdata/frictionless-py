# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from jsontableschema import Table
from ..register import profile


# Module API

@profile('ckan')
def ckan(errors, tables, source, **options):

    # Add tables
    url = '%s/api/3/action/package_search' % source
    data = requests.get(url).json()
    for package in data['result']['results']:
        for resource in package['resources']:
            if not resource['url'].endswith('.csv'):
                continue
            table = Table(resource['url'])
            extra = {
                'dataset': package['title'],
                'resource': resource['name'],
                'publisher': package['organization']['name']
            }
            tables.append({
                'table': table,
                'extra': extra,
            })
