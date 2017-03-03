from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect([
    {'source': 'data/valid.csv', 'schema': {'fields': [{'name': 'id'}, {'name': 'name'}]}},
    {'source': 'data/invalid.csv', 'preset': 'table'},
    {'source': 'data/datapackages/valid/datapackage.json', 'preset': 'datapackage'},
    {'source': 'data/datapackages/invalid/datapackage.json', 'preset': 'datapackage'},
], preset='nested')
pprint(report)
