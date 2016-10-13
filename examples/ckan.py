import requests
from pprint import pprint
from jsontableschema import Table
from goodtables import Inspector, profile

@profile('ckan')
def ckan_profile(errors, tables, source, **options):
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

inspector = Inspector(custom_profiles=[ckan_profile])
report = inspector.inspect('http://data.surrey.ca', profile='ckan')
pprint(report)
