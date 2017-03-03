from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect([
    {'source': 'data/datapackages/valid/datapackage.json'},
    {'source': 'data/datapackages/invalid/datapackage.json'},
], preset='datapackages')
pprint(report)
