from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect([
    'data/invalid.csv',
    {'source': 'data/valid.csv', 'schema': {'fields': [{'name': 'id'}, {'name': 'name'}]}},
], preset='tables')
pprint(report)
