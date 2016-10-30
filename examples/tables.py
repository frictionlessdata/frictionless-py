from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect([
    {'source': 'data/valid.csv', 'schema': {'fields': [{'name': 'id'}, {'name': 'name'}]}},
    {'source': 'data/invalid.csv'},
], preset='tables')
pprint(report)
